from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from schemas import PrescriptionResponse, UsageResponse
from collections import defaultdict

class AdherenceResult:
    def __init__(
        self,
        total_expected_doses: int,
        total_taken_doses: int,
        missed_doses: int,
        late_doses: int,
        missed_dates: List[datetime],
        late_dates: List[datetime],
        details: Dict[str, Any]
    ):
        self.total_expected_doses = total_expected_doses
        self.total_taken_doses = total_taken_doses
        self.missed_doses = missed_doses
        self.late_doses = late_doses
        self.missed_dates = missed_dates
        self.late_dates = late_dates
        self.details = details

def calculate_adherence(
    prescription: PrescriptionResponse,
    usage_logs: List[UsageResponse],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    late_threshold_hours: int = 2
) -> AdherenceResult:
    """
    Calculate prescription adherence based on usage logs.
    
    Args:
        prescription: The prescription to evaluate
        usage_logs: List of usage logs for this prescription
        start_date: Start date for evaluation (defaults to prescription start_date)
        end_date: End date for evaluation (defaults to current time or prescription end_date)
        late_threshold_hours: Number of hours after which a dose is considered late
    
    Returns:
        AdherenceResult containing adherence metrics and details
    
    Example:
        >>> from datetime import datetime
        >>> prescription = PrescriptionResponse(
        ...     id=1, user_id=1, medication_name="Aspirin", dosage="100mg",
        ...     pills_per_dose=1, times_per_day=2, start_date=datetime(2024, 1, 1),
        ...     end_date=datetime(2024, 1, 3), created_at=datetime.now(), updated_at=datetime.now()
        ... )
        >>> usage_logs = [
        ...     UsageResponse(id=1, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 8, 0)),
        ...     UsageResponse(id=2, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 20, 0)),
        ...     UsageResponse(id=3, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 8, 30))
        ... ]
        >>> result = calculate_adherence(prescription, usage_logs)
        >>> result.total_expected_doses
        6
        >>> result.total_taken_doses
        3
        >>> result.missed_doses
        3
    """
    # Set default dates if not provided
    if start_date is None:
        start_date = prescription.start_date
    if end_date is None:
        end_date = prescription.end_date or datetime.now()
    
    # Filter usage logs to the date range
    relevant_logs = [
        log for log in usage_logs 
        if start_date <= log.taken_at <= end_date
    ]
    
    # Group usage logs by date
    usage_by_date = defaultdict(list)
    for log in relevant_logs:
        usage_by_date[log.taken_at.date()].append(log)
    
    # Calculate expected and actual doses for each day
    current_date = start_date.date()
    end_date = end_date.date()
    
    missed_dates = []
    late_dates = []
    total_expected = 0
    total_taken = 0

    expected_doses_for_day = prescription.times_per_day
    
    while current_date <= end_date:
        actual_doses_for_day = len(usage_by_date[current_date])
        
        total_expected += expected_doses_for_day
        total_taken += actual_doses_for_day
        
        if actual_doses_for_day < expected_doses_for_day:
            # Some doses were missed
            missed_count = expected_doses_for_day - actual_doses_for_day
            for _ in range(missed_count):
                missed_dates.append(datetime.combine(current_date, datetime.min.time()))
        
        if actual_doses_for_day > expected_doses_for_day:
            # Extra doses were taken
            extra_count = actual_doses_for_day - expected_doses_for_day
            for _ in range(extra_count):
                late_dates.append(datetime.combine(current_date, datetime.min.time()))
        
        current_date += timedelta(days=1)
    
    # Calculate metrics
    missed = len(missed_dates)
    late = len(late_dates)

    
    return AdherenceResult(
        total_expected_doses=total_expected,
        total_taken_doses=total_taken,
        missed_doses=missed,
        late_doses=late,
        missed_dates=missed_dates,
        late_dates=late_dates,
        details={
            "times_per_day": prescription.times_per_day,
            "evaluation_period": {
                "start": start_date,
                "end": end_date
            }
        }
    ) 