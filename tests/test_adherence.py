import pytest
from datetime import datetime
from adherence import calculate_adherence
from schemas import PrescriptionResponse, UsageResponse

@pytest.fixture
def base_prescription():
    """Fixture to create a base prescription for testing"""
    return PrescriptionResponse(
        id=1,
        user_id=1,
        medication_name="Test Medication",
        dosage="100mg",
        pills_per_dose=1,
        times_per_day=2,  # twice daily
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 3),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def test_perfect_adherence(base_prescription):
    """Test when all doses are taken correctly"""
    usage_logs = [
        # Day 1
        UsageResponse(id=1, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 8, 0)),
        UsageResponse(id=2, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 20, 0)),
        # Day 2
        UsageResponse(id=3, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 8, 0)),
        UsageResponse(id=4, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 20, 0)),
        # Day 3
        UsageResponse(id=5, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 3, 8, 0)),
        UsageResponse(id=6, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 3, 20, 0)),
    ]

    result = calculate_adherence(base_prescription, usage_logs)
    
    assert result.total_expected_doses == 6  # 3 days × 2 doses
    assert result.total_taken_doses == 6
    assert result.missed_doses == 0
    assert result.late_doses == 0
    assert len(result.missed_dates) == 0
    assert len(result.late_dates) == 0

def test_missed_doses(base_prescription):
    """Test when some doses are missed"""
    usage_logs = [
        # Day 1 - perfect
        UsageResponse(id=1, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 8, 0)),
        UsageResponse(id=2, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 20, 0)),
        # Day 2 - missed evening dose
        UsageResponse(id=3, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 8, 0)),
        # Day 3 - missed both doses
    ]

    result = calculate_adherence(base_prescription, usage_logs)
    
    assert result.total_expected_doses == 6
    assert result.total_taken_doses == 3
    assert result.missed_doses == 3  # 1 on day 2, 2 on day 3
    assert result.late_doses == 0
    assert len(result.missed_dates) == 3
    assert len(result.late_dates) == 0

def test_extra_doses(base_prescription):
    """Test when extra doses are taken"""
    usage_logs = [
        # Day 1 - took 3 doses instead of 2
        UsageResponse(id=1, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 8, 0)),
        UsageResponse(id=2, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 12, 0)),
        UsageResponse(id=3, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 20, 0)),
        # Day 2 - perfect
        UsageResponse(id=4, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 8, 0)),
        UsageResponse(id=5, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 20, 0)),
    ]

    result = calculate_adherence(base_prescription, usage_logs)
    
    assert result.total_expected_doses == 6
    assert result.total_taken_doses == 5
    assert result.missed_doses == 1  # missed one on day 3
    assert result.late_doses == 1  # extra dose on day 1
    assert len(result.missed_dates) == 1
    assert len(result.late_dates) == 1

def test_once_daily():
    """Test once daily prescription"""
    prescription = PrescriptionResponse(
        id=1,
        user_id=1,
        medication_name="Test Medication",
        dosage="100mg",
        pills_per_dose=1,
        times_per_day=1,  # once daily
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 1, 3),
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

    usage_logs = [
        # Day 1 - perfect
        UsageResponse(id=1, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 8, 0)),
        # Day 2 - took twice
        UsageResponse(id=2, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 8, 0)),
        UsageResponse(id=3, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 20, 0)),
        # Day 3 - missed
    ]

    result = calculate_adherence(prescription, usage_logs)
    
    assert result.total_expected_doses == 3  # 3 days × 1 dose
    assert result.total_taken_doses == 3  # 1 + 2 + 0
    assert result.missed_doses == 1  # missed one on day 3
    assert result.late_doses == 1  # extra dose on day 2
    assert len(result.missed_dates) == 1
    assert len(result.late_dates) == 1

def test_custom_date_range(base_prescription):
    """Test adherence calculation for a custom date range"""
    usage_logs = [
        # Day 1
        UsageResponse(id=1, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 8, 0)),
        UsageResponse(id=2, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 1, 20, 0)),
        # Day 2
        UsageResponse(id=3, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 2, 8, 0)),
        # Day 3
        UsageResponse(id=4, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 3, 8, 0)),
        UsageResponse(id=5, user_id=1, prescription_id=1, taken_at=datetime(2024, 1, 3, 20, 0)),
    ]

    # Test only day 2
    result = calculate_adherence(
        base_prescription,
        usage_logs,
        start_date=datetime(2024, 1, 2),
        end_date=datetime(2024, 1, 2)
    )
    
    assert result.total_expected_doses == 2  # 1 day × 2 doses
    assert result.total_taken_doses == 1
    assert result.missed_doses == 1
    assert result.late_doses == 0 