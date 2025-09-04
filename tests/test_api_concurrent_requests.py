from tests.cloud_test_base import TestBase
from utils.test_utils import concurrent_tests


class TestAPIConcurrency(TestBase):

    TEST_USERNAME = "test"
    TEST_PASSWORD = "test"

    @concurrent_tests(100)
    async def test_concurrent_events(self):
        return await self.run_e2e_workflow(self.TEST_USERNAME, self.TEST_PASSWORD)
