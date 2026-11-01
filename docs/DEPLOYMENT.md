# 部署准备（尚未执行）

## 当前状态

已整理独立源码，两个工作流开关默认关闭。未创建 civilization-website，未更改 civilization-novel，未配置应用授权/Secrets，未运行云端工作流，未启用 Pages。
本地测试不代表 GitHub 权限、仓库规则或部署已验证。以下步骤等作者授权后才执行。

## 1. 建立公开网站仓库

创建 kevinzhang790510/civilization-website 为 Public，只提交本项目公开代码、文档、空数据和配置。不要复制任何小说文件或 Git 历史，原小说仓库始终保持 Private。

private-repository-setup 是不含真实小说或密钥的公开安装模板，可保留或单独存放。dist 随 ZIP 提供便于预览，但被 .gitignore 忽略，Pages 每次重新构建。

## 2. 最小权限 GitHub App

- 创建专用 GitHub App，无需 OAuth 用户授权或 Webhook。
- Repository permissions 仅 Contents: Read and write，以及 GitHub 必需的只读元数据权限。不申请 Actions write、Administration 等。
- 安装选择 Only select repositories → civilization-website；不要安装到小说仓库。
- 生成应用私钥，仅在**私有小说仓库** Settings → Secrets and variables → Actions 保存：
  - Variable WEBSITE_APP_ID：应用 App ID。
  - Secret WEBSITE_APP_PRIVATE_KEY：完整 PEM 私钥。
- 不把私钥写进项目、公开仓库、网页或日志。工作流生成短期安装令牌，任务结束撤销。
- 小说仓库 GITHUB_TOKEN 只读自身 contents；公开端没有读取小说仓库的 Secret。

使用 App 推送以触发公开仓库 push 工作流。不能用小说仓库的普通 GITHUB_TOKEN 替代跨仓库应用令牌。

## 3. 将模板安装到私有小说仓库（以后授权后再做）

| ZIP 模板 | 私有仓库目标 |
|---|---|
| private-repository-setup/publish-approved.yml | .github/workflows/publish-approved.yml |
| private-repository-setup/publication/export_approved.py | publication/export_approved.py |
| private-repository-setup/publication/chapters.json | publication/chapters.json |

不要把整个网站复制进私有仓库。清单初始保持 chapters: []。保护 main、发布清单、导出器和工作流的修改权限，确保作者明确批准。

## 4. 配置公开 Pages

- Settings → Pages → Build and deployment → Source 选 GitHub Actions。
- 确认 Actions 可运行所列 GitHub 官方 Actions。
- github-pages environment 仅允许 main 部署；若需要每次人工确认，可以加环境审批（会暂停自动部署等待批准）。
- 若仓库规则禁止 App 推送 main，为该 App 配置精确允许规则，或改用 PR 审核流程；不关闭全部保护。
- 工作流使用官方主要版本标签，正式启用前审阅并按要求锁定完整 commit SHA，降低供应链漂移风险。

## 5. 作者批准上线后打开开关

- 公开仓库 Variable PAGES_DEPLOY_ENABLED = true。
- 私有仓库 Variable PUBLICATION_EXPORT_ENABLED = true。
- 首次在公开仓库 Actions 手动运行部署空章节网站。
- 之后作者确认真实章节，按 PUBLICATION.md 更新正式文件与私有清单，推送 main：自动校验 → 推送公开 JSON → 公开 Actions 构建/部署。
- 空清单与空公开数据没有差异时不产生新提交，首次空站部署用公开工作流手动触发。
- 正式网址以 GitHub Actions 成功返回的 Pages URL 为准，目前没有生成或验证正式网址。

## 6. 验证与故障处理

检查私有校验成功、公开仓库只提交 approved JSON、Pages 部署成功，再刷新浏览器验证新目录。
校验失败不推送；公开构建失败不更新部署。推送冲突/权限错误会明确失败，修复后从私有 main 当前版本重新运行，不 force push。两边各自 concurrency 串行，不取消正在发布的版本。

私有工作流不上传整仓库/原稿，日志不输出正文，也不执行来自公开网站仓库的构建脚本。公开测试仅用临时合成文本；产物白名单仅 index.html、style.css、app.js、content.js、.nojekyll。
公开仓库维护者仍能修改公开数据，需限制写权限。关闭启用开关停止后续自动化，但不下线已发布站点；下线需另行关闭 Pages。

## 官方参考

- https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/trigger-a-workflow
- https://github.com/actions/create-github-app-token
