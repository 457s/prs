# 面向数据工作的开发工作台

---

## 简介

prs-项目集，集成shell工具链、AI工作区与个人项目等，持续迭代，持续使用。

## 使用说明

1. **部署说明**
   本项目需要部署至`$HOME/core/`目录下：

```bash
# Example
git clone https://github.com/457s/prs.git $HOME/core/prs
```

2. **终端配置**
   根据具体工作环境选择其一，win环境使用pwsh、linux环境使用bash等

```powershell
    $HOME\core\prs\pwsh\init.ps1
```

```bash
    $HOME/core/prs/bash/init.sh
```

## 目录介绍

| dir  | description |
| :--: | :---------: |
| bash |  终端配置   |
| pwsh |  终端配置   |
| ofme |  个人开发   |
| ofai |   AI开发    |
| env  |  环境变量   |
| bin  |  命令文件   |
