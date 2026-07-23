# MySQL application account

FoodPlatform API defaults to the non-root account `food_platform_app`. Account creation is an explicit administrator operation; the application and initialization scripts do not create users or change grants.

Choose a strong password locally and never place it in this repository. Run the following as a MySQL administrator after replacing the placeholder:

```sql
CREATE USER IF NOT EXISTS 'food_platform_app'@'localhost'
  IDENTIFIED BY 'replace_with_a_strong_local_password';

GRANT SELECT, INSERT, UPDATE, DELETE, EXECUTE
  ON food_platform.*
  TO 'food_platform_app'@'localhost';

SHOW GRANTS FOR 'food_platform_app'@'localhost';
```

For a backend running on another host, create a narrowly scoped host entry instead of using `%`. TLS should be enabled outside local development.

The account must not receive `DROP`, `ALTER`, `CREATE`, `CREATE USER`, `GRANT OPTION`, `FILE`, `PROCESS`, or other administrative privileges. Schema initialization remains a separate administrator workflow.

Store the real password only in ignored `backend/.env`:

```env
MYSQL_USER=food_platform_app
MYSQL_PASSWORD=your_local_secret
MYSQL_DATABASE=food_platform
```

Validate without printing the password:

```powershell
Set-Location D:\CodexProjects\FoodPlatform\backend
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Invoke-RestMethod http://127.0.0.1:8000/api/v1/health/ready
```

The expected MySQL component state is `ok`. A `503` with `mysql: error` means the service, host, account, password, database, or grants need checking; the API intentionally does not return the underlying credential error.
