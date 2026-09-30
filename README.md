# AI Web Pet

把想法、已有角色图或现实宠物照片，逐步做成能在网页里播放的宠物。

这是给 AI Agent 使用的 Skill，附 Python 校验/构建工具和原生 JavaScript 播放器。用户提供方向与审美判断，Agent整理角色与动作需求，生图与透明化允许在外部完成后回传。

**v0.1.0 首次发布候选。已做软件测试，真实第二角色录屏验证尚未进行。** 仓库不包含内部角色资产，测试色块不是宠物成功案例。

[English](docs/README.en.md) · [中文上手](docs/GETTING_STARTED.zh-CN.md) · [格式](references/format.md) · [测试与限制](docs/VALIDATION.md) · [来源](docs/PROVENANCE.md)

## 流程

Input → Pet Brief → Character Bible → 用户确认 Character Lock → Reference / Generation Handoff → Action Brief → 透明 PNG → clip/manifest → Web Player → QA

角色先锁定再扩动作；动作包含准备、发起、接触/主动作、反应与恢复，关键中间姿势必须实际绘制。等待型动作拆成enter/loop/exit。技术正确、视觉正确和用户接受分开记录。

## 安装

保持整个目录完整，把它作为 `ai-web-pet` 放入支持本地Skills的Agent技能目录，或让Agent直接读取 [SKILL.md](SKILL.md)。不同Agent的发现方式以各自说明为准。

对Agent说：“使用 ai-web-pet，帮我从这个想法/角色图/宠物照片开始，先整理角色需求，不要跳过定妆确认。”

没有图片或设定时，复制这句开始：

> 请使用 ai-web-pet 带我从零设计一只可以放在网页里的小宠物。
> 我现在没有角色图，也没有想好物种、风格、性格和配色。
> 请不要替我直接决定，每次只问我一个关键问题，并尽量给我 4～6 个清晰选项，同时保留“自定义”。
> 先把角色方向一步一步选出来，再告诉我下一步需要生成什么图片。

Agent 每次只问一个关键问题，尽量提供 4～6 个清晰选项及“自定义”，等你回答后再进入下一步。参见[自然引导流程](references/guided-intake.md)。


工具需要 Python 3.10+ 与 Pillow；测试还需支持 node --test 的 Node.js。播放器无 npm 依赖。

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/pet.py init ../my-pet
```

Windows PowerShell使用 `.venv\Scripts\Activate.ps1` 激活。接下来由Agent整理资料、取得真实确认并准备PNG。不要为通过检查而擅自批准pending内容。

```sh
python scripts/pet.py views ../my-pet
python scripts/pet.py validate ../my-pet
python scripts/pet.py build ../my-pet
python -m http.server 8000 --bind 127.0.0.1 --directory ../my-pet
```

访问 `http://127.0.0.1:8000/preview/<build_id>/index.html`，将build_id换成实际输出。file://不受支持。

## 网页接入

复制审阅后的preview/<build_id>为静态资源目录。运行时只需要manifest、PNG、player.mjs，不需要角色审批原文。

```html
<div id="pet"></div>
<script type="module">
import {loadPet} from './pet/player.mjs';
const pet = await loadPet({element:document.querySelector('#pet'),manifest:'./pet/manifest.json'});
// 动作名称来自自己的manifest：
// pet.play('rest');              // 进入并等待
// pet.requestStop();             // 当前段完成后退出
// pet.play('rest',{once:true});  // 完整播放一次
// pet.destroy();                 // 页面卸载时清理
</script>
```

业务事件由宿主绑定。v0不含自动anchor、万能抠图、骨架、复杂行为控制器、GUI、桌面安装、模型API合集或交付Package。PNG需提前透明化、对齐。

## 测试与反馈

```sh
python -m unittest discover -s tests -p 'test_*.py'
node --test tests/player.test.mjs
```

反馈请提供最小配置、命令、错误和期望，不上传无公开许可的角色素材或私人照片。源码与配套文档采用 [MIT License](LICENSE)。仓库不包含内部角色资产；角色形象、角色设定、品牌标识及用户回传素材不因本代码许可获得授权。
