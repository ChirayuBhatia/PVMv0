from django.test import TestCase
from .models import File


class FileModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        testdata = File.objects.create(fid=300, user=1, count=0, subject="Test", filename="test.txt", Printed=False)
        testdata.save()


def test_fid_content(self):
    todo = File.objects.get(id=1)

    expected_object_name = f'{todo.fid}'
    self.assertEquals(expected_object_name, 300)


def test_user_content(self):
    todo = File.objects.get(id=1)

    expected_object_name = f'{todo.user}'
    self.assertEquals(expected_object_name, 1)
