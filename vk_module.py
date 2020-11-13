from pprint import pprint

import vk_api


class VkUser:

    def __init__(self):
        self.token = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
        self.vk_api = vk_get_api = vk_api.VkApi(token=self.token).get_api()

    def get_user_info(self, user_id):
        user = self.vk_api.users.get(user_ids=user_id, fields='first_name, last_name, sex, bdate')
        return user[0]

    # def get_profile_photos(self, album_id="profile"):
    #     profile_photos_info_list = []
    #     downloaded_files = []
    #     url = f"https://api.vk.com/method/photos.get"
    #     parameters = {
    #         "owner_id": self.id,
    #         "album_id": album_id,
    #         "extended": 1,
    #         "photo_sizes": 1,
    #         "count": 5,
    #         "access_token": self.token,
    #         "v": 5.122
    #     }
    #     url_requests = "?".join((url, urlencode(parameters)))
    #     resp = requests.get(url_requests)
    #     self.photo_list = resp.json()["response"]["items"]

    def get_users_best_photos(self, user_id):
        parameters = {
            "owner_id": user_id,
            "extended": 1,
            "photo_sizes": 0,
            "count": 200,
            "access_token": self.token,
            "v": 5.77
        }
        photos_info = self.vk_api.photos.get(owner_id=user_id, album_id='profile',
                                             extended=1, count=1000, photo_sizes=0)
        photos_list = [elem['likes']['count'] for elem in photos_info['items']]

        return photos_list


if __name__ == '__main__':
    print(VkUser().get_user_info(206241))
    pprint(VkUser().get_users_best_photos(206241))

