from models.__init__ import CONN, CURSOR


class Site:
    all = {}

    CLASSIFICATIONS = ["Government", "Academic", "Medical"]

    def __init__(self, name, city, classification, id=None):
        self.id = id
        self.name = name
        self.city = city
        self.classification = classification

    def __repr__(self):
        return f"Site {self.id}: {self.name} | {self.city} | {self.classification} institution"

    @property
    def name(self):
        """Site name property"""
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str) and not name.isdigit() and len(name) > 1:
            self._name = name
        else:
            raise Exception(
                "Site's name must be a string at least two characters long."
            )

    @property
    def city(self):
        """Site city porperty"""
        return self._city

    @city.setter
    def city(self, city):
        if isinstance(city, str) and not city.isdigit() and len(city) > 1:
            self._city = city
        else:
            raise Exception("Site's city must be a string at least 2 characters long.")

    @property
    def classification(self):
        """Site classification property"""
        return self._classification

    @classification.setter
    def classification(self, classification):
        if classification in type(self).CLASSIFICATIONS:
            self._classification = classification
        else:
            raise Exception(
                "Site's classification must be one of the following strings: 'Government', 'Academic', 'Medical'"
            )

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS sites (
            id INTEGER PRIMARY KEY,
            name TEXT,
            city TEXT,
            classification TEXT)
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        sql = """
            DROP TABLE IF EXISTS sites
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def create(cls, name, city, classification):
        site = cls(name, city, classification)
        sql = """
            INSERT INTO sites (name, city, classification)
            VALUES (?, ?, ?)
        """
        CURSOR.execute(sql, (name, city, classification))
        CONN.commit()
        site.id = CURSOR.lastrowid
        cls.all[site.id] = site
        return site

    def update(self):
        sql = """
            UPDATE sites
            SET name = ?, city = ?, classification = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.city, self.classification, self.id))
        CONN.commit()

    def delete(self):
        for investigator in self.investigators():
            investigator.delete()
        sql = """DELETE FROM sites WHERE id = ?"""
        CURSOR.execute(sql, (self.id,))
        CONN.commit()
        del type(self).all[self.id]
        self.id = None

    @classmethod
    def instance_from_db(cls, row):
        if site := cls.all.get(row[0]):
            site.name = row[1]
            site.city = row[2]
            site.classification = row[3]
        else:
            site = cls(row[1], row[2], row[3], row[0])
            cls.all[site.id] = site
        return site

    @classmethod
    def get_all(cls):
        sql = """SELECT * FROM sites"""
        rows = CURSOR.execute(sql).fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @classmethod
    def find_by_id(cls, id):
        all_sites = cls.get_all()
        filtered = list(filter(lambda instance: instance.id == id, all_sites))
        return filtered[0] if len(filtered) else None

    @classmethod
    def find_by_name(cls, name):
        all_sites = cls.get_all()
        filtered = list(filter(lambda instance: instance.name == name, all_sites))
        return filtered[0] if len(filtered) else None

    def investigators(self):
        from models.investigator import Investigator

        sql = """
            SELECT * FROM investigators
            WHERE site_id = ?
        """
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        return [Investigator.instance_from_db(row) for row in rows]

    def projects(self):
        from models.project import Project

        sql = """
            SELECT * FROM projects
            INNER JOIN investigators
            ON projects.id = investigators.project_id
            WHERE investigators.site_id = ?
        """
        rows = CURSOR.execute(sql, (self.id,)).fetchall()
        projects = [Project.instance_from_db(row) for row in rows]
        return list(set(projects))
