import unittest
from datetime import datetime
from blog import app,db
from blog.models import User,Article


class TestBlogMethods(unittest.TestCase):

    # blog was set up correctly
    def test_login_render(self):
        tester = app.test_client(self)
        response = tester.get('/login', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def client_ok(self):
        tester = app.test_client(self)
        response = tester.get('/', content_type='html/text')
        print(response)
        #self.assertEqual(response.status_code, 200)
        assert b'Welcome To Cosmos Infinity' in response

    # login into the blog
    def test_posts_show_up_login_page(self):
        tester = app.test_client(self)
        response = tester.post(
            '/login',
            data=dict(username="admin", password="adminadmin"),
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 200)

    def test_contact_render(self):
        tester = app.test_client(self)
        response = tester.get('/contact', content_type='html/text')
        self.assertEqual(response.status_code, 200)

    def test_sign_up(self):
            tester = app.test_client(self)
            response = tester.post(
                '/signup',
                data=dict(username="adminbn",name__="admin123", lastname="123",email__="rohaib@gmail.com",password="adminadmin789"),
                follow_redirects=True
            )
            self.assertEqual(response.status_code, 200)

    def test_create_one_user_db(self):
        user1=  User(username='user_test_',
                            email='user_test__@cosmos.com',
                            password='user_test_hash_pass',
                            access = 0,
                            allow = False,
                            name='user_test_',
                            lastname='user_last_',
                            role = 1)
        db.session.add(user1)
        # Commit the changes for the users
        db.session.commit()
        user = User.query.filter_by(username='user_test_').first()
        #print(user.username)
        User.query.filter_by(username='user_test_').delete()
        db.session.commit()
        self.assertEqual(user, user1)

    def test_create_one_article_db(self):
        now = datetime.now()
        article = Article(id=1000,
                                  title='test_xxx',
                                  tags='test',
                                  article='test',
                                  url_image = 'test',
                                  timestamp = now,
                                  allow = False,
                                  author = 'author')
        db.session.add(article)
        # Commit the changes for the users
        db.session.commit()
        article_2 = Article.query.filter_by(title='test_xxx').first()
        #print(user.username)
        Article.query.filter_by(title='test_xxx').delete()
        db.session.commit()
        self.assertEqual(article, article_2)

if __name__ == '__main__':
    unittest.main()