import random

from metrics import GenericMetrics

class Metrics(GenericMetrics):
    def __init__(self, id, master_token, control_server_url, send_server_data):
        self.tot_request_time = 0
        self.is_busy = False

        super().__init__(id, master_token, control_server_url, send_server_data)
        
    def fill_data(self, data):
        self.fill_data_generic(data)
        data["cur_load"] = 1 if self.is_busy else 0
        self.cur_capacity_lastreport = 1 if self.is_busy else 0

    def start_req(self, request):
        self.num_requests_recieved += 1
        self.num_requests_working += 1
        num_prompt_tokens = len(request["prompt"].split())
        self.total_prompt_tokens += num_prompt_tokens

    def finish_req(self, request):
        self.num_requests_finished += 1
        self.num_requests_working -= 1
        self.tot_request_time += request["time_elapsed"]

    def error_req(self, request):
        self.num_requests_recieved -= 1
        self.num_requests_working -= 1

        num_prompt_tokens = len(request["prompt"].split())
        self.total_prompt_tokens -= num_prompt_tokens

    def report_req_stats(self, log_data):
        # self.tot_request_time += log_data["time_elapsed"]
        # self.cur_perf = self.img_size * (self.num_requests_finished / self.tot_request_time)
        self.curr_wait_time = log_data["wait_time"]
        self.cur_perf = self.img_size / (self.tot_request_time / self.num_requests_recieved) if (self.tot_request_time != 0 and self.num_requests_recieved != 0.0) else 0.0

        if self.curr_wait_time > 30.0:
            self.overloaded = True
        else:
            self.overloaded = False

    def send_data_condition(self):
        return (((random.randint(0, 9) == 3) or (self.total_prompt_tokens != self.cur_capacity_lastreport)) and self.model_loaded)