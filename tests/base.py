import gc
import json
import os
import re
import pytest
import warnings

import trio_mysql
from trio_mysql._compat import CPYTHON

class FakeUnittestcase:
    def assertEqual(self, a,b,r=None):
        assert a == b, (a,b,r)
    def assertIn(self, a,b,r=None):
        assert a in b, (a,b,r)
    def assertTrue(self, a,r=None):
        assert a, (a,r)
    def assertFalse(self, a,r=None):
        assert not a, (a,r)
    def assertRaises(self, *x):
        return pytest.raises(*x)
    def assertWarns(self, *x):
        return pytest.warns(*x)

class TrioMySQLTestCase(FakeUnittestcase):
    # You can specify your test environment creating a file named
    #  "databases.json" or editing the `databases` variable below.
    fname = os.path.join(os.path.dirname(__file__), "databases.json")
    if os.path.exists(fname):
        with open(fname) as f:
            databases = json.load(f)
    else:
        databases = [
            {"host":"localhost","user":"root",
             "passwd":"","db":"test_trio_mysql", "use_unicode": True, 'local_infile': True},
            {"host":"localhost","user":"root","passwd":"","db":"test_trio_mysql2"}]

    def mysql_server_is(self, conn, version_tuple):
        """Return True if the given connection is on the version given or
        greater.

        e.g.::

            if self.mysql_server_is(conn, (5, 6, 4)):
                # do something for MySQL 5.6.4 and above
        """
        server_version = conn.get_server_info()
        server_version_tuple = tuple(
            (int(dig) if dig is not None else 0)
            for dig in
            re.match(r'(\d+)\.(\d+)\.(\d+)', server_version).group(1, 2, 3)
        )
        return server_version_tuple >= version_tuple

    async def setUp(self):
        self.connections = []
        for params in self.databases:
            conn = trio_mysql.connect(**params)
            await conn.connect()
            self.connections.append(conn)

    async def tearDown(self):
        for connection in self.connections:
            await connection.aclose()

    async def safe_create_table(self, connection, tablename, ddl, cleanup=True):
        """create a table.

        Ensures any existing version of that table is first dropped.

        Also adds a cleanup rule to drop the table after the test
        completes.
        """
        async with connection.cursor() as cursor:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                await cursor.execute("drop table if exists `%s`" % (tablename,))
            await cursor.execute(ddl)
        if cleanup:
            self.addCleanup(self.drop_table, connection, tablename)

    async def drop_table(self, connection, tablename):
        async with connection.cursor() as cursor:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                await cursor.execute("drop table if exists `%s`" % (tablename,))

    def safe_gc_collect(self):
        """Ensure cycles are collected via gc.

        Runs additional times on non-CPython platforms.

        """
        gc.collect()
        if not CPYTHON:
            gc.collect()

class SkipTest(RuntimeError):
    pass

