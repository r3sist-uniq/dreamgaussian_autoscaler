import re
from logwatch import GenericLogWatch

class LogWatch(GenericLogWatch):
    def __init__(self, id, control_server_url, master_token):
        super().__init__(id=id, control_server_url=control_server_url, master_token=master_token, perf_test=None)
        self.ready_pattern = re.compile("Service ready, listening on http://127.0.0.1:5000")
        self.update_pattern = re.compile("Request processed in (\d+\.\d+)s")
    
    def check_model_ready(self, line):
        if self.ready_pattern.search(line):
            self.model_loaded()  # Signal that the model/service is ready
            return True
        return False
        
    def check_model_update(self, line):
        match = self.update_pattern.search(line)
        if match:
            processing_time = float(match.group(1))  # Capture processing time
            update_params = {"processing_time": processing_time}
            self.send_model_update(update_params)  # Send processing time as an update
            return True
        return False
   
    def handle_line(self, line):
        if self.check_model_ready(line):
            return
        elif self.check_model_update(line):
            return
