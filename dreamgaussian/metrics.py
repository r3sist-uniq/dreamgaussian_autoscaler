import random
from metrics import GenericMetrics

class Metrics(GenericMetrics):
    def __init__(self, id, master_token, control_server_url, send_server_data):
        self.models_generated = 0 # Number of models generated
        self.total_request_time = 0 # Total time spent processing requests

        super().__init__(id, master_token, control_server_url, send_server_data)

    def fill_data(self, data):
        self.fill_data_generic(data)
        # Update the load to reflect the number of models being processed
        data["current_load"] = self.models_generated
        self.cur_capacity_lastreport = self.models_generated

    def start_req(self, request):
        self.num_requests_received += 1
        self.num_requests_working += 1

    def finish_req(self, request):
        self.num_requests_finished += 1
        self.num_requests_working -= 1
        self.models_generated += 1  # Increment for each completed request
        self.total_request_time += request["time_elapsed"]  # Ensure time_elapsed is in seconds

    def error_req(self, request):
        # Adjust request counters on error without specific model metrics
        self.num_requests_received -= 1
        self.num_requests_working -= 1

    def report_req_stats(self, log_data):
        # Calculate models per second as the performance metric
        self.cur_perf = self.models_generated / self.total_request_time if self.total_request_time > 0 else 0
        self.curr_wait_time = log_data["wait_time"]
        self.overloaded = self.curr_wait_time > 30.0  # Mark as overloaded if wait time exceeds 30 seconds

    def send_data_condition(self):
        # Randomly send data or on significant change in generated models
        return (random.randint(0, 9) == 3) or (self.models_generated != self.cur_capacity_lastreport) and self.model_loaded
