from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, ValidationError, model_validator


class Rank(str, Enum):
    CADET = "cadet"
    OFFICER = "officer"
    LIEUTENANT = "lieutenant"
    CAPTAIN = "captain"
    COMMANDER = "commander"


class CrewMember(BaseModel):
    member_id: str = Field(..., min_length=3, max_length=10)
    name: str = Field(..., min_length=2, max_length=50)
    rank: Rank
    age: int = Field(..., ge=18, le=80)
    specialization: str = Field(..., min_length=3, max_length=30)
    years_experience: int = Field(..., ge=0, le=50)
    is_active: bool = True


class SpaceMission(BaseModel):
    mission_id: str = Field(..., min_length=5, max_length=15)
    mission_name: str = Field(..., min_length=3, max_length=100)
    destination: str = Field(..., min_length=3, max_length=50)
    launch_date: datetime
    duration_days: int = Field(..., ge=1, le=3650)
    crew: list[CrewMember] = Field(..., min_length=1, max_length=12)
    mission_status: str = "planned"
    budget_millions: float = Field(..., ge=1.0, le=10000.0)

    @model_validator(mode="after")
    def validate_mission(self) -> "SpaceMission":
        if not self.mission_id.startswith("M"):
            raise ValueError("Mission ID must start with 'M'")

        if not any(m.rank in (Rank.COMMANDER, Rank.CAPTAIN)
                   for m in self.crew):
            raise ValueError(
                "Mission must have at least one Commander or Captain")

        if self.duration_days > 365:
            experienced = sum(1 for m in self.crew if m.years_experience >= 5)
            if experienced < len(self.crew) / 2:
                raise ValueError(
                    "Long missions (> 365 days) need at least 50% "
                    "experienced crew (5+ years)")

        for member in self.crew:
            if not member.is_active:
                raise ValueError(f"Crew member '{member.name}' must be active")

        return self


def test_mission() -> None:
    print("Space Mission Crew Validation")
    print("=" * 41)

    crew = [
        CrewMember(
            member_id="SC001",
            name="Sarah Connor",
            rank=Rank.COMMANDER,
            age=42,
            specialization="Mission Command",
            years_experience=15,
        ),
        CrewMember(
            member_id="JS002",
            name="John Smith",
            rank=Rank.LIEUTENANT,
            age=35,
            specialization="Navigation",
            years_experience=8,
        ),
        CrewMember(
            member_id="AJ003",
            name="Alice Johnson",
            rank=Rank.OFFICER,
            age=29,
            specialization="Engineering",
            years_experience=5,
        )
    ]
    mission = SpaceMission(
        mission_id="M2024_MARS",
        mission_name="Mars Colony Establishment",
        destination="Mars",
        launch_date=datetime(2026, 7, 15, 9, 0),
        duration_days=900,
        crew=crew,
        budget_millions=2500.0,
    )
    print("\nValid mission created:")
    print(f"Mission: {mission.mission_name}")
    print(f"ID: {mission.mission_id}")
    print(f"Destination: {mission.destination}")
    print(f"Duration: {mission.duration_days} days")
    print(f"Budget: ${mission.budget_millions}M")
    print(f"Crew size: {len(mission.crew)}")
    print("Crew members:")
    for m in mission.crew:
        print(f"- {m.name} ({m.rank.value}) - {m.specialization}")
    print("=" * 41)

    try:
        bad_crew = [
            CrewMember(
                member_id="LO001",
                name="Liam Officer",
                rank=Rank.OFFICER,
                age=30,
                specialization="Medical",
                years_experience=4,
            ),
            CrewMember(
                member_id="LC002",
                name="Luna Cadet",
                rank=Rank.CADET,
                age=22,
                specialization="Communications",
                years_experience=1,
            ),
        ]
        SpaceMission(
            mission_id="M2024_FAIL",
            mission_name="Failed Mission",
            destination="Moon",
            launch_date=datetime(2026, 8, 1, 6, 0),
            duration_days=30,
            crew=bad_crew,
            budget_millions=100.0,
        )
    except ValidationError as e:
        print("\nExpected validation error:")
        for error in e.errors():
            print(f"- {error['msg']}")


if __name__ == "__main__":
    test_mission()
