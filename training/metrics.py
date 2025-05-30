import torch
from collections import defaultdict
import torch.distributed as dist

class RunningAverage:
    def __init__(self, total=0, count=0):
        self.total = total
        self.count = count

    def add(self, numbers: torch.Tensor):
        self.total += numbers.sum()
        self.count += numbers.numel()

    def get_average(self):
        if self.count == 0:
            return 0
        return self.total / self.count

    def __repr__(self):
        print(type(self.total), type(self.count))
        return f"RunningAverage(total={self.total}, count={self.count})"


class RunningAverageTensor:
    def __init__(self, total: torch.Tensor, count: torch.Tensor):
        assert total.shape == count.shape
        self.total = total
        self.count = count

    def add(self, dim, index: torch.Tensor, values: torch.Tensor):
        self.total.index_add_(dim, index, values)
        self.count.index_add_(dim, index, torch.ones_like(values))

    def get_average(self):
        total = self.total
        count = self.count
        # Perform element-wise division where count is not zero, else put zero
        return torch.where(count != 0, total / count, torch.zeros_like(total))

    def get_total_average(self):
        total = self.total.sum()
        count = self.count.sum()
        return 0 if count == 0 else total / count

    def __repr__(self):
        print(type(self.total), type(self.count))
        return f"RunningAverageTensor(total={self.total}, count={self.count})"

    def to(self, device):
        self.total = self.total.to(device)
        self.count = self.count.to(device)


class Aggregator:
    """
    Calculation in which all metrics for every sample in the validation set are gathered
    in all devices.
    """
    def __init__(self, group_names: list[str], device):
        self.group_names = group_names
        def ra_factory():
            total = torch.zeros(len(group_names), device=device)
            count = torch.zeros(len(group_names), device=device)
            return RunningAverageTensor(total, count)

        self._ra = defaultdict(ra_factory)  # (metric_name, group_id) -> RunningAverage

    def to(self, device):
        for v in self._ra.values():
            v.to(device)

    def add_batch(
        self,
        batch_group_ixs: torch.Tensor,  # Every element is the index of the group to which
                                        # the corresponding sample belongs, shape (batch_size,)
        batch_metrics: dict[str, torch.Tensor],  # metric_name -> tensor with batch_size elements
        accelerator
    ):
        metric_names = list(batch_metrics.keys())
        batch_metrics["group_ixs"] = batch_group_ixs
        # Gather all metrics in all devices
        gathered_metrics = accelerator.gather_for_metrics(batch_metrics)
        for metric_name in metric_names:
            values = gathered_metrics[metric_name]
            group_ixs = gathered_metrics["group_ixs"]
            # Update the running statistics of every group
            self._ra[metric_name].add(0, group_ixs.flatten(), values.flatten())

    def gather_for_metrics(self, run, batch_metrics):
        current_device = torch.cuda.current_device()
        process_group = run.device_mesh.get_group(mesh_dim="dp")
        group_size = dist.get_world_size(group=process_group)
        dp_rank = run.dp_rank
        tp_rank = run.tp_rank
        gathered_metrics = {}
        for key in batch_metrics.keys():
            if batch_metrics[key] is not None:
                gathered_metrics[key] = [torch.zeros_like(batch_metrics[key]).to(current_device) for _ in range(group_size)]
            else:
                gathered_metrics[key] = [None for _ in range(group_size)]
                
        # gathered_metrics = {
        #     key: [torch.zeros_like(batch_metrics[key]).to(current_device) \
        #             for _ in range(group_size)] for key in batch_metrics.keys()
        # }
        for key in batch_metrics.keys():
            if dp_rank == 0 and tp_rank == 0:
                dist.gather(batch_metrics[key].to(current_device), gather_list=gathered_metrics[key], group=process_group)
            elif dp_rank != 0 and tp_rank == 0:
                dist.gather(batch_metrics[key].to(current_device), dst=0, group=process_group)

        # Convert each list of tensors into a single tensor
        for key in batch_metrics.keys():
            if batch_metrics[key] is not None:
                gathered_metrics[key] = torch.cat(gathered_metrics[key], dim=0).to(torch.cuda.current_device())

        return gathered_metrics
    
    def add_batch_2(
        self,
        batch_group_ixs: torch.Tensor,  # Every element is the index of the group to which
                                        # the corresponding sample belongs, shape (batch_size,)
        batch_metrics: dict[str, torch.Tensor],  # metric_name -> tensor with batch_size elements
        global_rank,
        run,
    ):
        metric_names = list(batch_metrics.keys())
        batch_metrics["group_ixs"] = batch_group_ixs
        # Gather all metrics in all devices, where acclelerator.gather_for_metrics was called
        gathered_metrics = self.gather_for_metrics(run, batch_metrics)

        for metric_name in metric_names:
            values = gathered_metrics[metric_name]
            group_ixs = gathered_metrics["group_ixs"]
            # Update the running statistics of every group
            self._ra[metric_name].add(0, group_ixs.flatten(), values.flatten())

    def key_to_string(self, key):
        metric_name, group_id = key
        group_name = self.group_names[int(group_id)]
        return "/".join((metric_name, group_name))

    def get_average(self) -> tuple[dict[str, float], dict[str, float]]:
        metrics_by_group = {}
        metrics_total = {}
        for metric_name, ra in self._ra.items():
            av = ra.get_average()
            metrics_by_group.update({
                self.key_to_string((metric_name, i)): av[i]
                for i in range(len(self.group_names))
                if ra.count[i] > 0
            })
            metrics_total[metric_name] = ra.get_total_average()

        return metrics_total, metrics_by_group


