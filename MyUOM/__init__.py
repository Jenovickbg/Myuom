try:
    import pymysql
    pymysql.install_as_MySQLdb()
except Exception:
    # Le projet peut encore démarrer sans PyMySQL installé.
    # L'installation sera requise pour se connecter à MySQL.
    pass


