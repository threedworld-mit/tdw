from typing import List
from tdw.add_ons.model_verifier.model_tests.model_test import ModelTest
from tdw.output_data import OutputData, LogMessage


class ModelReport(ModelTest):
    """
    Send `send_model_report` and get a basic report on the model.
    """

    def start(self) -> List[dict]:
        """
        :return: A list of commands to start the test.
        """

        return [{"$type": "send_model_report",
                 "name": self._record.name,
                 "url": self._record.get_url(),
                 "id": 0,
                 "scale_factor": self._record.scale_factor}]

    def on_send(self, resp: List[bytes]) -> List[dict]:
        """
        :param resp: The response from the build.

        :return: A list of commands to continue or end the test.
        """

        self.done = True
        for i in range(len(resp) - 1):
            r_id = OutputData.get_data_type_id(resp[i])
            if r_id == "logm":
                log_message = LogMessage(resp[i])
                self.reports.append(log_message.get_message_type() + ": " + log_message.get_message())
        return []

