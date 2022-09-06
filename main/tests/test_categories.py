from nis import cat
from main.models import Category
from django.contrib.auth.models import User
from rest_framework import status
import pytest
from model_bakery import baker

@pytest.fixture
def create_category(api_client):
    def do_create_category(category):
        return api_client.post('/main/categories/', category)
    return do_create_category

@pytest.mark.django_db
class TestCreateCategory:

    # @pytest.mark.skip
    def test_if_user_is_anonymous_returns_401(self, create_category):
        response = create_category({'title': 'a'})
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


    def test_if_user_is_not_admin_returns_403(self, authenticate, create_category):
        authenticate()
        response = create_category({'title': 'a'})
        assert response.status_code == status.HTTP_403_FORBIDDEN


    def test_if_data_is_invalid_returns_400(self, authenticate, create_category):
        authenticate(is_staff=True)
        response = create_category({'title': ''})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert response.data['title'] is not None

    
    def test_if_data_is_valid_returns_201(self, authenticate, create_category):
        authenticate(is_staff=True)
        response = create_category({'title': 'a'})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['id'] > 0


@pytest.mark.django_db
class TestRetrieveCategory:
    def test_if_category_exists_returns_200(self, api_client):
        category = baker.make(Category)
        response = api_client.get(f'/main/categories/{category.id}/')
        assert response.status_code == status.HTTP_200_OK
        assert response.data == {
            'id': category.id,
            'title': category.title,
            'posts_count': 0
        }