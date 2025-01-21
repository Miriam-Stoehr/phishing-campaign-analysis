import csv
import io
from typing import List, Tuple
from gophish import Gophish

class GophishClient:
    """Handles connection to the Gophish API and data fetching."""

    def __init__(self, api_key: str, host: str = "https://127.0.0.1:3333") -> None:
        self.client = Gophish(api_key, host=host, verify=False)

    def fetch_campaigns(self) -> List[object]:
        return self.client.campaigns.get()

    def fetch_campaign_details(self, campaign_id: int) -> object:
        return self.client.campaigns.get(campaign_id)


class CampaignDataProcessor:
    """Processes campaign data into CSV format."""

    def __init__(self, campaigns: List[object]) -> None:
        self.campaigns = campaigns

    def process_campaigns(self) -> Tuple[str, str]:
        results_buffer = io.StringIO()
        events_buffer = io.StringIO()

        results_writer = self._initialize_csv_writer(results_buffer, [
            "campaign_id", "campaign_name", "template_id", "template_name", "status", "ip",
            "latitude", "longitude", "send_date", "reported", "modified_date", "email",
            "first_name", "last_name", "position"
        ])
        events_writer = self._initialize_csv_writer(events_buffer, [
            "campaign_id", "campaign_name", "template_id", "template_name", "email",
            "time", "message", "details"
        ])

        for campaign in self.campaigns:
            self._process_single_campaign(campaign, results_writer, events_writer)

        return results_buffer.getvalue(), events_buffer.getvalue()

    @staticmethod
    def _initialize_csv_writer(buffer: io.StringIO, headers: List[str]) -> csv.writer:
        writer = csv.writer(buffer)
        writer.writerow(headers)
        return writer

    def _process_single_campaign(self, campaign, results_writer, events_writer) -> None:
        campaign_id = campaign.id
        campaign_name = campaign.name
        template_id = campaign.template.id if campaign.template else None
        template_name = campaign.template.name if campaign.template else None

        results = campaign.results
        events = campaign.timeline
        send_dates = {e.email: e.time for e in events if e.message == "Email Sent"}
        reported_statuses = {e.email: True for e in events if e.message == "Email Reported"}

        for result in results:
            modified_date = max((e.time for e in events if e.email == result.email), default=None)
            send_date = send_dates.get(result.email)
            reported = reported_statuses.get(result.email, False)
            results_writer.writerow([
                campaign_id, campaign_name, template_id, template_name, result.status, result.ip,
                result.latitude, result.longitude, send_date, reported, modified_date,
                result.email, result.first_name, result.last_name, result.position
            ])

        for event in events:
            events_writer.writerow([
                campaign_id, campaign_name, template_id, template_name, event.email,
                event.time, event.message, event.details
            ])
