def replaceReadPaths():
    import replaceReadPath as rrp
    reload(rrp)
    rrp.Window().show()
    
def fromRedToDefault():
    import redToDefault as rd
    reload(rd)
    rd.change()