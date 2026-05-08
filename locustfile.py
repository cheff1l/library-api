from locust import HttpUser, between, task


class LibraryApiUser(HttpUser):
    wait_time = between(0.5, 1.5)

    @task
    def login(self):
        with self.client.post(
            "/auth/login",
            json={"username": "student", "password": "password123"},
            name="POST /auth/login",
            catch_response=True,
        ) as response:
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
                return

            try:
                body = response.json()
            except ValueError:
                response.failure("Response is not valid JSON")
                return

            if "access_token" not in body or "refresh_token" not in body:
                response.failure("Token pair is missing in response")
