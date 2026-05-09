"""Structured diffractometer calculation results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DAFSolution:
    """Named result of solving a diffractometer HKL or angle calculation."""

    motor_angles: dict[str, Any]
    pseudo_angles: dict[str, Any]
    hkl: Any
    qerror: float
    q_vector: Any
    q_vector_norm: Any
    dhkl: Any
    structure_factor: Any

    @classmethod
    def from_engine(cls, engine: Any) -> "DAFSolution":
        return cls(
            motor_angles={
                "mu": engine.Mu,
                "eta": engine.Eta,
                "chi": engine.Chi,
                "phi": engine.Phi,
                "nu": engine.Nu,
                "del": engine.Del,
            },
            pseudo_angles={
                "twotheta": engine.ttB1,
                "theta": engine.tB1,
                "alpha": engine.alphain,
                "qaz": engine.qaz,
                "naz": engine.naz,
                "tau": engine.taupseudo,
                "psi": engine.psipseudo,
                "beta": engine.betaout,
                "omega": engine.omega,
            },
            hkl=engine.hkl_calc,
            qerror=float(engine.qerror),
            q_vector=engine.Qshow,
            q_vector_norm=engine.Qnorm,
            dhkl=engine.dhkl,
            structure_factor=engine.FHKL,
        )

    def success(self, max_error: float) -> bool:
        return self.qerror <= max_error

    def to_angle_dict(self) -> dict[str, Any]:
        return {
            **self.motor_angles,
            **self.pseudo_angles,
            "hklnow": self.hkl,
            "qerror": "{0:.2e}".format(self.qerror),
        }

    def to_legacy_export_list(self) -> list[Any]:
        """Return the historical ``DAF.export_angles()`` positional format."""
        return [
            self.motor_angles["mu"],
            self.motor_angles["eta"],
            self.motor_angles["chi"],
            self.motor_angles["phi"],
            self.motor_angles["nu"],
            self.motor_angles["del"],
            self.pseudo_angles["twotheta"],
            self.pseudo_angles["theta"],
            self.pseudo_angles["alpha"],
            self.pseudo_angles["qaz"],
            self.pseudo_angles["naz"],
            self.pseudo_angles["tau"],
            self.pseudo_angles["psi"],
            self.pseudo_angles["beta"],
            self.pseudo_angles["omega"],
            self.hkl,
            "{0:.2e}".format(self.qerror),
        ]
