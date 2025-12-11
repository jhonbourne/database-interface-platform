import { useState } from 'react';
import { Upload, Image, message } from 'antd';
import { PlusOutlined } from '@ant-design/icons';

const getBase64 = file =>
  new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.readAsDataURL(file);
    reader.onload = () => resolve(reader.result);
    reader.onerror = error => reject(error);
  });

export default function FileUpload({ fileList, setFileList, maxCount = 1 }) {
  const [previewOpen, setPreviewOpen] = useState(false);
  const [previewImage, setPreviewImage] = useState('');

  const handlePreview = async file => {
    if (!file.url && !file.preview) {
      file.preview = await getBase64(file.originFileObj);
    }
    setPreviewImage(file.url || file.preview);
    setPreviewOpen(true);
  };

  const handleChange = ({ fileList: newFileList }) => setFileList(newFileList);

  const uploadButton = (
    <div>
      <PlusOutlined />
      <div style={{ marginTop: 8 }}>Upload</div>
    </div>
  );

  return (
    <>
      <Upload
        listType="picture-card"
        fileList={fileList}
        onPreview={handlePreview}
        onChange={handleChange}
        maxCount={maxCount}
      >
        {fileList.length >= maxCount ? null : uploadButton}
      </Upload>

      {previewImage && (
        <Image
          style={{ display: 'none' }}
          preview={{
            open: previewOpen,
            onOpenChange: visible => setPreviewOpen(visible),
            afterOpenChange: visible => !visible && setPreviewImage(''),
          }}
          src={previewImage}
        />
      )}
    </>
  );
}
