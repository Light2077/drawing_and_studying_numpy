"""
将某个ipynb文件转换为markdown文件

"""
import os
import re
import json
import base64


class Notebook:
    def __init__(self, notebook_path, markdown_dir=".", image_dir_name="images"):
        
        # 读取.ipynb文件数据
        self.cells = list()
        with open(notebook_path, 'r', encoding='utf8') as f:
            notebook_dict = json.load(f)
            for cell_dict in notebook_dict.get('cells'):
                self.cells.append(Cell(self, cell_dict))

        self.notebook_path = notebook_path
        self.notebook_dict = notebook_dict
        
        # self.markdown_name = os.path.split(self.notebook_path)[-1].split('.')[0]
        self.markdown_name = os.path.splitext(self.notebook_path)[0]
        self.markdown_dir = markdown_dir
        self.markdown_path = os.path.join(self.markdown_dir, self.markdown_name + ".md")
        
        self.img_save_dir = os.path.join(self.markdown_dir, image_dir_name)
        self.img_num = 1
    
    def save_img(self, image):
        # 创建图片文件夹
        if not os.path.isdir(self.img_save_dir):
            os.makedirs(self.img_save_dir)
        
        # 图片编码为二进制
        img_data = base64.b64decode(image)

        # img_name == "demoname_plot_1.png"
        img_name = f"{self.markdown_name}_plot_{self.img_num}.png"
        img_path = os.path.join(self.img_save_dir, img_name)

        with open(img_path, 'wb') as f:
            f.write(img_data)
        
        self.img_num += 1
        # img_name = os.path.split(img_path)[-1]
        
        return f"![](./images/{img_name})\n"
    
    def text(self):
        res = ""
        for cell in self.cells:
            res += cell.text()
        return res
    
    def to_markdown(self, save=False):
        text = self.text()
        if save:
            if not os.path.isdir(self.markdown_dir):
                os.makedirs(self.markdown_dir)

            with open(self.markdown_path, 'w', encoding='utf8') as f:
                f.write(text)
        return text


class Cell(dict):
    def __init__(self, notebook, cell_dict):
        super().__init__()
        self.update(cell_dict)
        
        self.notebook = notebook
        
        # self.cell_type = cell_dict['cell_type']
        # self.source = cell_dict['source']
        # self.outputs = cell_dict.get('outputs')
    def __getattr__(self, key):
        return self[key]
    
    def __setattr__(self, key, value):
        self.__dict__[key] = value
    
    # def __repr__(self):
    #    return f"{self.idx} cell_type: {self.cell_type}"
        
    def markdown_text(self):
        return "".join(self.source) + '\n'
    
    def code_text(self, text, code_type='python'):
        if text:
            return f"```{code_type}\n{text}```\n"
        return ""
        # text = "".join(self.source)
        # return f"```{code_type}\n{text}\n```\n"
    
    def outputs_text(self):
        text = ""
        imgs = list()
        for output in self.outputs:
            # print的输出
            if output['output_type'] == 'stream':
                text = text +  "".join(output['text'])
                continue
            
            # 错误的输出
            if output['output_type'] == "error":
                tmp = "\n".join(output['traceback'])
                tmp = re.sub(r'\x1b.*?m', '', tmp)
                text = text + tmp + '\n'
                # text += f"```\n{tmp}\n```\n"
                continue

            output_data = output['data']
            
            # 图片类型的输出
            image = output_data.get('image/png')
            if image:
                # 保存图片到特定文件夹
                # img_data = base64.b64decode(image)
                markdown_img = self.notebook.save_img(image)
                imgs.append(markdown_img)
                continue
                
            # 文本类型的输出
            text_plain = output_data.get('text/plain')
            if text_plain:
                text = text +  "".join(text_plain) + "\n"
                
        text = self.code_text(text, code_type='')
        text += "".join(imgs)
        
        return text
    
    def text(self):
        if self.cell_type == 'markdown':
            return self.markdown_text()
        
        if self.cell_type == "code":
            c_text = "".join(self.source) + "\n"
            res = self.code_text(c_text)
            
            res += self.outputs_text()
            return res


"""
# 单文件转换
notebook = Notebook('demo.ipynb', '/home/study/markdowns')
res = notebook.to_markdown(save=True)
"""

# 将当前文件夹下的ipynb文件转换为md文件
if __name__ == "__main__":
    for file_name in os.listdir():
        if file_name.split('.')[-1] != 'ipynb':
            continue
        notebook = Notebook(file_name)
        notebook.to_markdown(save=True)
