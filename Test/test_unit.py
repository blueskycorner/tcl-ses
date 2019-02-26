import handler   # The code to test

def test_getMonth():
    assert handler.getMonth('2019-02_TCL.jpg') == 'de Février'
    assert handler.getMonth('2021-02_TCL.jpg') == 'de Février'
    assert handler.getMonth('2021-03_TCL.jpg') == 'de Mars'
    assert handler.getMonth('2021-04_TCL.jpg') == "d'Avril"
    assert handler.getMonth('2020-05_TCL.jpg') == 'de Mai'
    assert handler.getMonth('2021-06_TCL.jpg') == 'de Juin'
    assert handler.getMonth('2020-07_TCL.jpg') == 'de Juillet'
    assert handler.getMonth('2019-08_TCL.jpg') == "d'Août"