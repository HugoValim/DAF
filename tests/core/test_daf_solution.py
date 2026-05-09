from daf.core.solution import DAFSolution


def test_solution_from_engine_exposes_named_angles():
    class Engine:
        Mu = 1.0
        Eta = 2.0
        Chi = 3.0
        Phi = 4.0
        Nu = 5.0
        Del = 6.0
        ttB1 = 7.0
        tB1 = 8.0
        alphain = 9.0
        qaz = 10.0
        naz = 11.0
        taupseudo = 12.0
        psipseudo = 13.0
        betaout = 14.0
        omega = 15.0
        hkl_calc = [1.0, 1.0, 1.0]
        qerror = 1e-9
        Qshow = [0.1, 0.2, 0.3]
        Qnorm = 0.4
        dhkl = 0.5
        FHKL = 0.6

    solution = DAFSolution.from_engine(Engine())

    assert solution.motor_angles["mu"] == 1.0
    assert solution.pseudo_angles["alpha"] == 9.0
    assert solution.hkl == [1.0, 1.0, 1.0]
    assert solution.success(1e-4) is True
    assert solution.to_angle_dict()["hklnow"] == [1.0, 1.0, 1.0]
    assert solution.to_legacy_export_list() == [
        1.0,
        2.0,
        3.0,
        4.0,
        5.0,
        6.0,
        7.0,
        8.0,
        9.0,
        10.0,
        11.0,
        12.0,
        13.0,
        14.0,
        15.0,
        [1.0, 1.0, 1.0],
        "1.00e-09",
    ]
