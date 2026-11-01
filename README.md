# 《文明之痕》独立小说阅读网站

保留现有首页设计、八部作品入口、第一部《石之永恒》介绍和目录、阅读界面、字号/行距、三种主题、全屏/沉浸、浏览器阅读进度及移动端布局。

**交付状态：只有本地源码和未激活配置。没有获准公开章节，没有创建仓库、改动小说仓库或部署网站。自动同步尚未启用，也未在 GitHub 完成端到端验证。**

## 独立运行

需要 Python 3.10+（推荐 3.12），无第三方 Python 或 JavaScript 依赖。浏览器无需 ChatGPT、Sites、登录或 API 密钥。无需 npm install；package.json 仅提供可选命令别名。

```sh
python3 scripts/build.py
python3 -m http.server 8080 --directory dist
```

打开 http://localhost:8080 。Windows 可用 `py -3` 替换 `python3`。
也可以直接打开随附的 dist/index.html，但建议使用 HTTP 服务获得一致的本地存储行为。

验证：

```sh
python3 -m unittest discover -s tests -v
```

## 项目结构

| 路径 | 用途 |
|---|---|
| web/index.html、style.css、app.js | 保留的网页、样式及阅读器源码 |
| published/chapters.json | 公开数据，当前为空；未来只接收审核通过的导出结果 |
| scripts/build.py | 仅白名单网页文件及公开章节构建至 dist |
| scripts/export_approved.py | 私有仓库导出器开发副本；公开部署不调用它读取私有仓库 |
| .github/workflows/pages.yml | 公开仓库构建及 Pages 部署，默认关闭 |
| private-repository-setup/ | 将来由作者安装到私有仓库的模板，当前不执行 |
| docs/DEPLOYMENT.md | 授权、仓库准备及启用步骤 |
| docs/PUBLICATION.md | 审批清单、格式、更新及撤回规则 |
| tests/ | 临时合成安全测试，不是小说章节，不进入网站 |
| dist/ | 可直接托管的构建结果，当前没有章节 |
| package.json | 可选 npm 命令，无 npm 依赖 |

金字塔、太阳、沙丘均由 CSS 绘制；箭头和状态标记为文本符号，字体用系统字体。没有遗漏的外部图片、图标包、远程字体或 CDN 依赖。未来新增图片需建立公开资源白名单；当前正文导出器拒绝图片与链接，不复制私有附件。

## 内容架构

私有 kevinzhang790510/civilization-novel → 私有 Actions 校验、导出 → 公开 kevinzhang790510/civilization-website 的 published/chapters.json → 公开 Actions 构建 → GitHub Pages。

小说仓库保持 Private。公开端不持有读取私有小说仓库的凭据。GitHub App 仅有网站仓库 Contents write，应用私钥仅保存于私有小说仓库 Actions Secret。私有工作流的 GITHUB_TOKEN 只读自身仓库；短期应用令牌仅推送审核后的 JSON。

发布需要正式目录、作者定稿标记、发布清单及字节校验值全部吻合。清单为空时，不发布任何正文。详见 docs/PUBLICATION.md。

## 保留与限制

- 不影响现有 Sites 项目；压缩包不含 Sites 身份、凭据或 Git 历史。
- 进度与设置保留原 localStorage 键，但域名变化时浏览器不会自动迁移旧域名数据；不跨设备同步。
- 当前仅第一部有阅读数据接口；另七部保留筹备中入口。未来开放其他部需扩展正式目录白名单及阅读路由；当前拒绝 volume != 1。
- 正文按纯文本段落渲染，不执行 HTML/Markdown；段落间空一行，单个换行由浏览器折叠。
- 保留“作者预览”标识，正式上线前可单独确认移除；没有改变首页设计。
- Actions 是待授权启用的真实配置模板，不能声称已运行自动同步。
- 部署成功后读者刷新/重新打开看到更新；不提供已打开页面实时推送。

详细步骤见 docs/DEPLOYMENT.md。当前不要打开两个启用开关。
