from django.conf import settings
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible
from fdfs_client.client import Fdfs_client


@deconstructible
class FastDFSStorage(Storage):
    ''' 是为了重写 Storage 类，完成自定义的数据保存！'''

    def __init__(self, base_url=None, client_conf=None):
        """
        初始化
        :param base_url: 用于构造图片完整路径使用，图片服务器的域名
        :param client_conf: FastDFS客户端配置文件的路径
        """
        if base_url is None:
            # 指定访问域名！按照这个域名的形式进行访问！
            base_url = settings.FDFS_URL
        self.base_url = base_url
        if client_conf is None:
            # 获取连接的配置文件！也就是 utils 下的client.conf
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

    def _open(self, name, mode='rb'):
        """
        用不到打开文件，所以省略
        """
        pass

    def _save(self, name, content):
        """
        在FastDFS中保存文件
        :param name: 传入的文件名
        :param content: 文件内容
        :return: 保存到数据库中的FastDFS的文件名
        """
        ''' 
        ret 返回信息类型如下所示！
       {
            'Storage IP': '192.168.43.108',
             'Status': 'Upload successed.',
             'Uploaded size': '24.00KB',
             'Group name': 'group1',
             'Remote file_id': 'group1/M00/00/00/wKgrbFsyQUeAcbLKAABh_hLB1MA524.jpg',
             'Local file name': '0.jpg'
        }'''

        # 加载配置文件！
        client = Fdfs_client(self.client_conf)
        # 保存文件！返回的是详细的字典形式信息
        ret = client.upload_by_buffer(content.read())
        if ret.get("Status") != "Upload successed.":
            raise Exception("upload file failed")
        # 获取服务器存储的位置！
        file_name = ret.get("Remote file_id")
        return file_name

    def url(self, name):
        """
        返回文件的完整URL路径
        :param name: 数据库中保存的文件名,上个函数返回的 file_name
        :return: 完整的URL
        """
        # 返回的是完整的url
        return self.base_url + name  # http://image.meiduo.site:8888/group1/M00/00/02/CtM3Glsx73iABkf0AAJFCjh_asQ005.jpg

    def exists(self, name):
        """
        判断文件是否存在，FastDFS可以自行解决文件的重名问题
        所以此处返回False，告诉Django上传的都是新文件
        :param name:  文件名
        :return: False
        """
        return False
