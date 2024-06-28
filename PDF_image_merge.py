from pypdf import PdfWriter,PdfReader
from PIL import Image
import os, io

#Environment: Python 3.6.2, pydpf 4.2.0 pillow 7.2.0

# 将img_path目录下的所有图片文件另存于save_pdf_path目录下，名字不变
def image_to_pdf(img_path, save_pdf_path):
    print("将图片转换为pdf文件")
    file_list = os.listdir(img_path)
    for x in file_list:
        if x.lower().endswith(('.jpg', '.jpeg', '.png')):
            pdf_name = x.split('.')[0]
            im1 = Image.open(os.path.join(img_path, x))
            save_pdf_name = os.path.join(save_pdf_path, pdf_name + ".pdf")
            im1.save(save_pdf_name, "PDF", resolution=100.0)
            print(f"已将 {os.path.join(img_path, x)} 另存为为 {save_pdf_name}, 分辨率为100.0")
        else:
            pass
    print("图片转换为pdf文件完成")


# 测试pdf_list中文件是否能逐页成功加载，为[]时检查python文件所在目录下所有pdf文件
def test_pdf_load(pdf_list=[]):
    print("将检查以下pdf文件是否能成功加载：")
    python_file_path = os.path.dirname(os.path.abspath(__file__))
    test_files = []
    try:
        if pdf_list == []:
            file_list = os.listdir(python_file_path)
            for file in file_list:
                if file.lower().endswith(('.pdf')):
                    test_files.append(os.path.join(python_file_path, file))
                else:
                    pass
        else:
            for file in pdf_list:
                if file.lower().endswith(('.pdf')):
                    test_files.append(os.path.join(python_file_path, file))
                else:
                    pass
        # print(test_files)
        for file in test_files:
            pdf_reader = PdfReader(file)
            print("检查:", file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                print(f"Page {page_num + 1} loaded successfully.")
            print()
    except Exception as e:
        print(f"An error occurred: {e}")

# 返回一个由图像转换的pdf页面对象
def create_pdf_page_from_image(image_file, resolution=100.0):
    # Open the image file
    image = Image.open(image_file)
    
    # Calculate the dimensions in PDF units (1/72 inch per unit)
    width, height = image.size
    pdf_width = width * resolution / 72
    pdf_height = height * resolution / 72
    
    # Create a blank PDF page with the size of the image
    pdf_writer = PdfWriter()
    pdf_writer.add_blank_page(width=pdf_width, height=pdf_height)
    
    # Save the image data to a temporary stream in PDF format
    pdf_stream = io.BytesIO()
    image.save(pdf_stream, format="PDF", resolution=resolution)
    pdf_stream.seek(0)
    
    # Read the image PDF stream as a PDF page
    image_pdf_reader = PdfReader(pdf_stream)
    image_page = image_pdf_reader.pages[0]
    
    return image_page

# file_list为空时合并python文件所在目录下所有pdf文件，merge_pdf_and_image为True时，将图片也进行合并
# file_list不为空时合并列表中.pdf, jpg, jpeg, png文件
def merge_pdf(file_list=[], output_pdf_file_name="merged_document.pdf", merge_pdf_and_image=False):
    merger = PdfWriter()
    python_file_path = os.path.dirname(os.path.abspath(__file__))
    count = 0
    if file_list == []:
        file_list = os.chdir(python_file_path)
        print("已合并：")
        for file in os.listdir(python_file_path):
            if ".pdf" in file:
                try:
                    input_file = open(file, "rb")
                except:
                    print("Error: 无法打开文件：", file, "已跳过")
                    continue
                merger.append(input_file)
                input_file.close()
                print(os.path.join(python_file_path, file))
                count += 1
            elif file.lower().endswith(('.jpg', '.jpeg', '.png')) and merge_pdf_and_image:
                pdf_from_image = create_pdf_page_from_image(os.path.join(python_file_path, file))
                merger.add_page(pdf_from_image)
                print(os.path.join(python_file_path, file))
                count += 1
            else:
                pass
    
    # 合并指定pdf文件
    else:
        print("已合并以下pdf文件：")
        for file in file_list:
            file = os.path.join(python_file_path, file)
            if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                try:
                    pdf_from_image = create_pdf_page_from_image(os.path.join(python_file_path, file))
                    merger.add_page(pdf_from_image)
                except: 
                    print("Error: 文件不存在或错误：", file, "已跳过")
                    continue

            elif file.lower().endswith(('.pdf')):
                try:
                    input_file = open(file, "rb")
                    merger.append(input_file)
                    input_file.close()
                except: 
                    print("Error: 文件不存在或错误：", file, "已跳过")
                    continue

            else:
                print("Error: 文件格式错误：", file, "已跳过")
                continue

            print(file)
            count += 1
            

    # 输出保存合并后的pdf文件
    output = open(os.path.join(python_file_path, output_pdf_file_name), "wb")
    merger.write(output)
    merger.close()
    output.close()
    print(f"共合并{count}个pdf文件")



def split_pdf(input_pdf_path, page_numbers, output_directory):
    """
    Splits a PDF file at the specified page numbers and saves the split PDFs.

    :param input_pdf_path: Path to the input PDF file.
    :param page_numbers: List of page numbers to split the PDF at.
    :param output_directory: Directory where the split PDFs will be saved.
    """
    print("当前工作目录：" , os.getcwd())

    pdf_reader = PdfReader(input_pdf_path)
    total_pages = len(pdf_reader.pages)
    # Ensure page_numbers are sorted and unique
    page_numbers = sorted(set(page_numbers))
    if page_numbers[-1] >= total_pages:
        raise ValueError(f"Page number {page_numbers[-1]} is greater than the total number of pages in the PDF file ({total_pages}).")
    else:
        print(f"Splitting PDF at page numbers: {page_numbers}")
        
    # Add start and end points to the split points
    split_points = [0] + page_numbers + [total_pages]
    for i in range(len(split_points) - 1):
        pdf_writer = PdfWriter()
        start, end = split_points[i], split_points[i + 1]
        
        for page_num in range(start, end):
            pdf_writer.add_page(pdf_reader.pages[page_num])
        
        output_pdf_path = os.path.join(output_directory, f'split_{i + 1}.pdf')
        with open(output_pdf_path, 'wb') as output_pdf_file:
            pdf_writer.write(output_pdf_file)
        
        print(f"Saved split PDF: {output_pdf_path}")


# print(os.path.abspath(__file__))    # 获取当前python文件绝对路径
# print(os.path.dirname(os.path.abspath(__file__)))  # 获取当前python文件所在目录，结尾无\  windows下用\  linux下用/
if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    file_list = ["1.jpg","2.jpg","1.pdf", "2.pdf", "3.pdf","4.pdf","5.pdf","6.pdf","7.pdf","8.pdf","9.pdf","10.pdf"]
    # file_list为空时(默认)合并python文件所在目录下所有pdf文件，merge_pdf_and_image为True时，将图片也进行合并
    # file_list不为空时合并列表中.pdf, jpg, jpeg, png文件
    merge_pdf(file_list, merge_pdf_and_image=True)
    split_pdf("merged_document.pdf", [1, 3, 5, 11], '.')
    # test_pdf_load(pdf_list)
