import os
import time
import fitz
from PIL import Image
import logging
import base64
from datetime import datetime
from openai import OpenAI


class PDFProcessor:
    def __init__(self, output_dir: str, api_key: str, api_base: str, model_path: str):
        """
        初始化处理器
        :param output_dir: 输出目录
        :param api_key: OpenAI API密钥
        :param api_base: API基础URL
        :param model_path: 模型路径
        """
        self.output_dir = output_dir
        self.model_path = model_path

        # 设置OpenAI客户端
        self.client = OpenAI(
            api_key=api_key,
            base_url=api_base
        )

        # 设置日志和汇总文件
        self.log_file = os.path.join(output_dir, f"process_log_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
        self.summary_file = os.path.join(output_dir, "all_results.md")
        self._setup_logger()

    def _setup_logger(self):
        """设置日志记录器"""
        os.makedirs(self.output_dir, exist_ok=True)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.log_file, encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _process_image(self, image_path: str) -> str:
        """使用OpenAI处理图像"""
        self.logger.info(f"开始处理图像: {image_path}")
        try:
            # 读取图像并转换为base64
            with open(image_path, 'rb') as file:
                image = "data:image/jpeg;base64," + base64.b64encode(file.read()).decode('utf-8')

            question = '''请分析图片中的内容并按以下规则转换为markdown格式：

            1. 对于表格内容：
               - 使用标准markdown表格语法
               - 保持表格完整结构，包括表头和分隔符
               - 使用 | 作为列分隔符，确保列对齐
               - 表头下方必须添加 |---|---|---| 格式的分隔行
               - 确保单元格内容完整，不要截断

            2. 对于普通文本内容：
               - 保持原有段落结构
               - 使用换行分隔不同段落

            3. 对于图片内容：
               - 简单清晰描述图片内容

            4. 对于列表内容：
               - 列表使用 - 格式

            5. 注意事项：
               - 忽略页眉和装饰性分隔线
               - 保持内容的层次结构
               - **不要添加任何解释性文字！！**
               - 按照内容的原有顺序进行转换'''
            # 调用OpenAI API
            self.logger.info("调用OpenAI API...")
            chat_response = self.client.chat.completions.create(
                model=self.model_path,
                messages=[{
                    "role": "user",
                    "content": [
                        {"type": "text", "text": question},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image,
                            },
                        },
                    ],
                }],
                extra_body={
                    "stop_token_ids": [151645, 151643]
                }
            )

            result = chat_response.choices[0].message.content
            self.logger.info("API调用成功")
            return result

        except Exception as e:
            self.logger.error(f"API调用错误: {e}")
            return f"处理失败: {str(e)}"

    def _process_page(self, pdf_document, page_num: int):
        """处理单个页面"""
        page_start_time = time.time()
        self.logger.info(f"\n开始处理第 {page_num + 1}/{pdf_document.page_count} 页...")

        # 获取页面图像
        page = pdf_document[page_num]
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # 保存临时图片文件
        temp_img_path = os.path.join(self.output_dir, f"temp_{page_num}.png")
        img.save(temp_img_path, "PNG")

        try:
            # 处理图像
            result = self._process_image(temp_img_path)

            # 将结果追加到汇总文件
            self._append_to_summary(page_num, result)

            self.logger.info(f"第 {page_num + 1} 页处理完成并添加到汇总文件")

        except Exception as e:
            self.logger.error(f"处理第 {page_num + 1} 页时发生错误: {e}")

        finally:
            # 删除临时图片
            if os.path.exists(temp_img_path):
                os.remove(temp_img_path)
                self.logger.debug(f"已删除临时文件: {temp_img_path}")

        page_end_time = time.time()
        processing_time = page_end_time - page_start_time
        self.logger.info(f"第 {page_num + 1} 页处理完成，耗时: {processing_time:.2f}秒")

    def _append_to_summary(self, page_num: int, content: str):
        """将结果追加到汇总文件"""
        with open(self.summary_file, 'a', encoding='utf-8') as f:
            f.write(f"\n{'=' * 50}\n")
            f.write(f"第 {page_num + 1} 页内容:\n")
            f.write(f"{'=' * 50}\n")
            f.write(content)
            f.write("\n")

    def process_pdf(self, pdf_path: str):
        """处理整个PDF文档"""
        self.logger.info(f"开始处理PDF: {pdf_path}")
        self.logger.info(f"使用模型: {self.model_path}")
        self.logger.info(f"输出目录: {self.output_dir}")

        # 创建或清空汇总文件
        with open(self.summary_file, 'w', encoding='utf-8') as f:
            f.write(f"PDF处理结果汇总\n")
            f.write(f"处理时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"源文件: {pdf_path}\n")
            f.write(f"使用模型: {self.model_path}\n\n")

        try:
            pdf_document = fitz.open(pdf_path)
            total_pages = pdf_document.page_count
            self.logger.info(f"PDF总页数: {total_pages}")

            for page_num in range(total_pages):
                self._process_page(pdf_document, page_num)

            self.logger.info(f"PDF处理完成。结果已保存到: {self.summary_file}")

        except Exception as e:
            self.logger.error(f"处理PDF时发生错误: {e}")
        finally:
            pdf_document.close()


def main():
    # 配置参数
    output_dir = "output"
    api_key = "token-abc123"  # 你的API密钥
    api_base = "http://192.168.1.121:8000/v1"  # API基础URL
    model_path = "/home/xxx/data/modeldata/ckpt/MiniCPM-V-2_6"  # 模型路径
    pdf_path = "./shenzhen-2022.PDF"  # PDF文件路径

    # 创建处理器实例
    processor = PDFProcessor(output_dir, api_key, api_base, model_path)

    # 处理PDF
    processor.process_pdf(pdf_path)


if __name__ == "__main__":
    main()