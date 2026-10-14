import unittest,tempfile,io,base64,os,json
from pathlib import Path
from unittest.mock import patch
from types import SimpleNamespace
from image_backends.toapis_async import ToAPIsClient,build_request,normalize_origin
from image_backends import backend_toapis

class ToAPIsBackendTests(unittest.TestCase):
    def params(self):return dict(model='gpt-image-2-vip',prompt='fixture',size='1024x576',quality='low',n=1)
    def client(self,d):
        c=ToAPIsClient('fixture-only',state_dir=d);c._asset=lambda url:b'fixture';return c
    def test_only_approved_https_origin(self):
        self.assertEqual(normalize_origin('https://toapis.com/v1/'),'https://toapis.com')
        for host in ['http://toapis.cn','https://evil.test','https://toapis.cn/v1/v1','https://u:p@toapis.cn']:
            with self.assertRaises(ValueError):normalize_origin(host)
    def test_ratio_and_explicit_tier(self):
        body,refs=build_request(self.params());self.assertEqual(body['size'],'16:9');self.assertEqual(body['quality'],'low');self.assertEqual(body['resolution'],'1K');self.assertEqual(refs,[])
    def test_unsupported_options_fail_before_requests(self):
        for extra in [dict(n=2),dict(mask='mask'),dict(background='transparent'),dict(output_format='jpeg'),dict(input_fidelity='high')]:
            with self.assertRaises(ValueError):build_request({**self.params(),**extra})
    def test_completed_task_reuses_id_without_second_post(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.client(d);calls=[]
            def query(path,body=None,content_type=None):
                calls.append((path,body));return {'id':'fixture-id'} if body else {'status':'completed','result':{'data':[{'url':'https://assets.test/image.png'}]}}
            c._json=query;c.generate(**self.params());c.generate(**self.params());self.assertEqual(sum(b is not None for _,b in calls),1)
    def test_uncertain_submit_blocks_new_generation(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.client(d);calls=[]
            def query(*args):calls.append(args);raise TimeoutError()
            c._json=query
            with self.assertRaises(RuntimeError):c.generate(**self.params())
            with self.assertRaises(RuntimeError):c.generate(**self.params())
            self.assertEqual(len(calls),1)
    def test_failed_task_does_not_restart(self):
        with tempfile.TemporaryDirectory() as d:
            c=self.client(d);calls=[]
            def query(path,body=None,content_type=None):
                calls.append((path,body));return {'id':'fixture-id'} if body else {'status':'failed'}
            c._json=query
            with self.assertRaises(RuntimeError):c.generate(**self.params())
            with self.assertRaises(RuntimeError):c.generate(**self.params())
            self.assertEqual(sum(b is not None for _,b in calls),1)
    def test_backend_uses_original_png_writer(self):
        from PIL import Image
        b=io.BytesIO();Image.new('RGB',(16,16),(25,90,70)).save(b,format='PNG');encoded=base64.b64encode(b.getvalue()).decode();calls=[]
        fake=SimpleNamespace(generate=lambda **kwargs:(calls.append(kwargs) or SimpleNamespace(data=[SimpleNamespace(b64_json=encoded)])))
        with tempfile.TemporaryDirectory() as d,patch.object(backend_toapis,'ToAPIsClient',return_value=fake),patch.dict(os.environ,{'TOAPIS_API_KEY':'fixture-only'}):
            p=backend_toapis.generate('fixture',aspect_ratio='16:9',output_dir=d,filename='test')
            self.assertEqual(Image.open(p).size,(16,16));self.assertEqual(calls[0]['size'],'1024x576');self.assertEqual(calls[0]['quality'],'low');self.assertEqual(calls[0]['n'],1)
    def test_backend_rejects_untested_model_and_size(self):
        with self.assertRaises(ValueError):backend_toapis.generate('x',model='gpt-image-2')
        with self.assertRaises(ValueError):backend_toapis.generate('x',image_size='4K')
