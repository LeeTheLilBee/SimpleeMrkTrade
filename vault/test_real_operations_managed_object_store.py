import hashlib
import pytest
from vault.real_operations_managed_object_store import PrivateManagedCiphertextStore
from vault.real_operations_encrypted_storage import StorageError

KEY="objects/"+"a"*48
class FakeClient:
    def __init__(self):
        self.saved={}
        self.last=None
    def put_object(self,**kwargs):
        self.last=kwargs
        if kwargs["Key"] in self.saved: raise RuntimeError("precondition failed")
        self.saved[kwargs["Key"]]=kwargs
    def get_object(self,**kwargs):
        row=self.saved[kwargs["Key"]]
        class Body:
            def read(self,n): return row["Body"][:n]
        return {"Body":Body(),"Metadata":row["Metadata"],"ContentLength":len(row["Body"])}

def test_create_only_and_verified_ciphertext():
    client=FakeClient()
    store=PrivateManagedCiphertextStore(client=client,bucket="private-vault-test")
    encrypted=b"VLT1"+b"x"*40
    store.put_if_absent(KEY,encrypted)
    assert client.last["IfNoneMatch"]=="*"
    assert client.last["ServerSideEncryption"]=="AES256"
    assert store.get(KEY)==encrypted
    with pytest.raises(RuntimeError):
        store.put_if_absent(KEY,encrypted)
    client.saved[KEY]["Metadata"]["ciphertext-sha256"]="0"*64
    with pytest.raises(StorageError,match="integrity"):
        store.get(KEY)

def test_rejects_plaintext_and_invalid_keys():
    store=PrivateManagedCiphertextStore(client=FakeClient(),bucket="private-vault-test")
    with pytest.raises(StorageError): store.put_if_absent(KEY,b"PDF document")
    with pytest.raises(StorageError): store.put_if_absent("../secret",b"VLT1encrypted")
    with pytest.raises(StorageError): store.get("../secret")
    with pytest.raises(StorageError): PrivateManagedCiphertextStore(client=None,bucket="private-vault-test")
