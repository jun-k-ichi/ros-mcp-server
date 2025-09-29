# ROS MCP Server 🧠⇄🤖

![Static Badge](https://img.shields.io/badge/ROS-Available-green)
![Static Badge](https://img.shields.io/badge/ROS2-Available-green)
![Static Badge](https://img.shields.io/badge/License-Apache%202.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![GitHub Repo stars](https://img.shields.io/github/stars/robotmcp/ros-mcp-server?style=social)
![GitHub last commit](https://img.shields.io/github/last-commit/robotmcp/ros-mcp-server)

<!-- README.md (English, default) -->
<p align="right">
  <a href="./README.md">English</a> |
  <a href="./README.ja.md">日本語</a>
</p>

<p align="center">
  <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/framework.png"/>
</p>

ROS-MCP-Serverは、大規模言語モデル LLM（Claude、GPT、Geminiなど）を既存のロボットに接続し、双方向のAI連携を実現します。

既存のロボットのソースコードに変更を加えることなく、次の事が可能になります：
- 🗣 **自然言語でロボットに命令する** → 命令はROS/ROS2コマンドに変換
- 👀 **AIにあらゆる可視性を与える** → トピックの購読、サービスの呼び出し、センサーデータの読み取り、ロボットの状態をリアルタイムで監視  


### ✅ 主なメリット  

- **ロボットコードの変更なし** → 必要なのは `rosbridge` ノードの追加のみ 
- **真の双方向コミュニケーション** → LLMはロボットを*制御*することも、ROSで起きていること（センサー、トピック、パラメーター）を*観察*することもできる  
- **ROS1 & ROS2 support** → どちらのバージョンでもすぐに使えます  
- **MCP-compatible** → MCP対応LLM（Claude Desktop、Gemini、ChatGPT、その他）と統合できます  

## 🎥 実例  

🖥️ **例 - NVIDIA Isaac SimでMOCAモバイルマニピュレータを制御する**  
Claude Desktopにコマンドを入力し、MCPサーバーを使用してシミュレートされたロボットを直接動かします。  

<p align="center">
  <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/result.gif" />
</p>  

---
🐕 **例 - 自然言語でUnitree Goを制御する**  ([video](https://youtu.be/RW9_FgfxWzs?si=8bdhpHNYaupzi9q3))  
MCPサーバーは、Claudeがロボットのカメラからの画像を解釈し、人間の自然言語コマンドに基づいてロボットに命令することを可能にする。

<p align="left">
  <img src="https://contoro.com/asset/media/demo_go2.gif" />
</p>  

---
🏭 **例 - 産業用ロボットのデバッグ** ([Video](https://youtu.be/SrHzC5InJDA))  
- 産業用ロボットに接続することで、LLMはすべてのROSトピックとサービスを監視し、ロボットの状態を評価することができます。 
- 事前に情報がないため、MCPサーバーはLLMがカスタムトピックとサービスタイプ、およびその定義の詳細を照会できるようにします（00:28）。 
- 自然言語だけを使って、オペレーターはロボットのテストとデバッグのためにカスタムサービスを呼び出す(01:42)。 

<p align="center">
  <a href="https://contoroinc.sharepoint.com/:v:/s/SandboxNewBusiness/EVh2t2_YG9BEl-Bw-8k6xucBcEv7XebJv1MtqLTIfrQpig?e=deu3YO">
    <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/Contoro_robot.png" width="400" alt="Testing and debugging an industrial robot" />
  </a>
</p>

---

## ⚙️ ROS MCPサーバーの機能  

- **トピック、サービス、メッセージタイプの一覧表示** → ロボットのROS環境で利用可能なすべての情報を探索します。  
- **タイプ定義の可視化（カスタムも含む）** → あらゆるメッセージの構造を理解する。  
- **トピックの公開/購読** → コマンドを送信したり、ロボットデータをリアルタイムでストリームする。 
- **サービス呼び出し（カスタム含む）** → ロボット機能を直接トリガーする。 
- **パラメータの取得/設定** → ロボットの設定をその場で読み取り、調整する。  
- 🔜 **アクションサポート** → ROS アクションのサポート予定。  
- 🔜 **権限コントロール** → より安全な配備のためにアクセスを管理する。  

---

## 🛠 はじめに  

MCPサーバーはバージョンに関係なく（ROS1またはROS2）、すべてのMCP互換LLMで動作します。 

<p align="center">
  <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/MCP_topology.png"/>
</p>  

### インストール  

詳細な手順については、[インストールガイド](docs/installation.md)に従ってください：  
1. リポジトリをクローンする  
2. `uv` と `rosbridge` をインストールする  
3. Claude Desktop（またはMCP対応クライアント）をインストールする  
4. ROS MCPサーバーに接続するようにクライアントを設定する  
5. ターゲットロボットで `rosbridge` を起動する 

---

## 📚 その他の例とチュートリアル  

私たちの[例](examples)をブラウズして、実際に動いているサーバーをご覧ください。 
私たちは、新しい例や連携に関するコミュニティのPRを歓迎します！  

---

## 🤝 貢献  

私たちはあらゆる種類の貢献を大歓迎です：  
- バグ修正とドキュメントの更新  
- 新機能（アクションサポート、パーミッションなど）  
- その他の例とチュートリアル  

[寄稿ガイドライン](docs/contributing.md)をチェックし、**good first issue**とタグ付けされた課題を見て、始めましょう。  

---

## 📜 ライセンス  

このプロジェクトのライセンスは[Apache License 2.0](LICENSE)です。 
