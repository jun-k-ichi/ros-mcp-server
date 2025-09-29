# インストレーション・ガイド

> ⚠️ **前提条件**: あなたのマシンにローカルにインストールされたROSか、ROSがインストールされたロボット/コンピュータにネットワーク経由でアクセスする必要があります。このMCPサーバーはロボット上のROSシステムに接続するため、ROSが動作する環境が必要です。

インストールは以下の手順です：
- MCPサーバーのインストール
  - このリポジトリをクローンする
  - uv (Python 仮想環境マネージャ) をインストールする。
- 言語モデルクライアントのインストールと設定
  - 任意の言語モデルクライアントをインストールする(Claude Desktopでデモしています)
  - クライアントがMCPサーバーを実行し、起動時に自動的に接続するように設定する。
- Rosbridgeのインストールと起動


以下は、それぞれの手順の詳細です。

---
# 1. MCPサーバーをインストールする（LLMを実行するホストマシン上）

## 1.1. リポジトリのクローン

```bash
git clone https://github.com/robotmcp/ros-mcp-server.git
```

クローンされたディレクトリへの**絶対パス**に注意してください - 後で言語モデルクライアントを設定するときに必要になります。

---

## 1.2. UV（Python仮想環境マネージャ）のインストール

以下のいずれかの方法で[`uv`](https://github.com/astral-sh/uv)をインストールできます：

<details>
<summary><strong>方法 A: シェルインストーラ</strong></summary>

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

</details>

<details>
<summary><strong>方法 B: pip を使う</strong></summary>

```bash
pip install uv
```

</details>

---

# 2. 言語モデルクライアントのインストールと設定 

MCP をサポートしている LLM クライアントであれば、どれでも使用できます。テストと開発には**Claude Desktop**を使用しています。

<details>
<summary><strong>Linux (Ubuntu)</strong></summary>

## 2.1. ダウンロード Claude Desktop 
- コミュニティがサポートするインストール手順に従ってください。 [claude-desktop-debian](https://github.com/aaddrick/claude-desktop-debian)

## 2.2. Claude DesktopがMCPサーバーを起動するように設定する
- `claude_desktop_config.json` ファイルを見つけて編集する：
- (ファイルが存在しない場合は作成する)
```bash
~/.config/Claude/claude_desktop_config.json
```

- JSONファイルの`"mcpServers"`セクションに以下を追加する。
- `<ABSOLUTE_PATH>`は、`ros-mcp-server`フォルダへの**完全な絶対パス**に置き換えてください（注意：ホームディレクトリを表す `~` は、JSONファイルでは機能しない場合があります）：

```json
{
  "mcpServers": {
    "ros-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/<ABSOLUTE_PATH>/ros-mcp-server",
        "run",
        "server.py"
      ]
    }
  }
}
```

## 2.3. 接続テスト
- クロードデスクトップを起動し、接続状態を確認する。
- ros-mcp-serverがツールのリストに表示されているはずです。

<p align="center">
  <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/connected_mcp.png" width="500"/>
</p>

## 2.4. トラブルシューティング
- claude_desktop_config.json` を正しく設定しても `ros-mcp-server` が表示されない場合は、以下のコマンドを使用して Claude Desktop を完全にシャットダウンしてから再起動してみてください。これは、Claude Desktop のキャッシュの問題である可能性があります。
```bash
# Claude Desktopのプロセスを完全に終了する
pkill -f claude-desktop
# あるいは
killall claude-desktop

# Claude Desktopを再起動する
claude-desktop
```

</details>

<details>
<summary><strong>MacOS</strong></summary>

## 2.1. ダウンロード Claude Desktop 
- [claude.ai](https://claude.ai/download)からダウンロード

## 2.2. Claude DesktopがMCPサーバーを起動するように設定する
- `claude_desktop_config.json` ファイルを見つけて編集する：
- (ファイルが存在しない場合は作成する)
```bash
~/Library/Application\ Support/Claude/claude_desktop_config.json
```

- JSONファイルの`"mcpServers"`セクションに以下を追加する。
- `<ABSOLUTE_PATH>`は、`ros-mcp-server`フォルダへの**完全な絶対パス**に置き換えてください（注意：ホームディレクトリを表す `~` は、JSONファイルでは機能しない場合があります）：

```json
{
  "mcpServers": {
    "ros-mcp-server": {
      "command": "uv",
      "args": [
        "--directory",
        "/<ABSOLUTE_PATH>/ros-mcp-server",
        "run",
        "server.py"
      ]
    }
  }
}
```

## 2.3. 接続テスト
- Claude Desktopを起動し、接続状態を確認する。 
- ros-mcp-serverがツールのリストに表示されているはずです。

<p align="center">
  <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/connected_mcp.png" width="500"/>
</p>

</details>

<details>
<summary><strong>Windows (Using WSL)</strong></summary>


## 2.1. ダウンロード Claude Desktop 
この場合、Claude は Windows 上で動作し、MCP サーバは WSL 上で動作します。リポジトリをクローンし、[WSL](https://apps.microsoft.com/detail/9pn20msr04dw?hl=en-US&gl=US)にUVをインストールしたと仮定します。

- [claude.ai](https://claude.ai/download)からダウンロード

## 2.2. Claude DesktopがMCPサーバーを起動するように設定する
- `claude_desktop_config.json` ファイルを見つけて編集する：
- (ファイルが存在しない場合は作成する)
```bash
~/.config/Claude/claude_desktop_config.json
```

- JSONファイルの`"mcpServers"`セクションに以下を追加する
- `<ABSOLUTE_PATH>`は、`ros-mcp-server`フォルダへの**完全な絶対パス**に置き換えてください（注意：ホームディレクトリを表す `~` は、JSONファイルでは機能しない場合があります）：
- **完全な WSL パス** を `uv` インストールに設定します（例：`/home/youruser/.local/bin/uv`）。
- 正しい**WSLディストリビューション名**を使用してください（例えば、`"Ubuntu-22.04"`）。

```json
{
  "mcpServers": {
    "ros-mcp-server": {
      "command": "wsl",
      "args": [
        "-d", "Ubuntu-22.04",
        "/home/youruser/.local/bin/uv",
        "--directory",
        "/<ABSOLUTE_PATH>/ros-mcp-server",
        "run",
        "server.py"
      ]
    }
  }
}
```

## 2.3. 接続テスト
- Claude Desktopを起動し、接続状態を確認する。
- ros-mcp-serverがツールのリストに表示されているはずです。

<p align="center">
  <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/connected_mcp.png" width="500"/>
</p>

</details>
---

# 3. rosbridgeのインストールと実行 (ROSが動作するターゲットロボット上で)
<details>
<summary><strong>ROS 1</strong></summary>

## 3.1. インストール `rosbridge_server`

このパッケージは、MCPがWebSocket経由でROSまたはROS 2と通信するために必要です。ROSを実行しているマシンと同じマシンにインストールする必要があります。


For ROS Noetic
```bash
sudo apt install ros-noetic-rosbridge-server
```
<details>
<summary>For other ROS Distros</summary>

```bash
sudo apt install ros-${ROS_DISTRO}-rosbridge-server
```
</details>

```bash
sudo apt install ros-humble-rosbridge-server
```



## 3.2. ROS環境でrosbridgeを起動します：


```bash
roslaunch rosbridge_server rosbridge_websocket.launch
```
> ⚠️ 特にカスタムメッセージやカスタムサービスを使用している場合は、起動する前にROSワークスペースを`source`することを忘れないでください。

</details>

<details>
<summary><strong>ROS 2</strong></summary>


## 3.1. インストール `rosbridge_server`

このパッケージは、MCPがWebSocket経由でROSまたはROS 2と通信するために必要です。ROSを実行しているマシンと同じマシンにインストールする必要があります。


For ROS 2 Humble
```bash
sudo apt install ros-humble-rosbridge-server
```
<details>
<summary>For other ROS Distros</summary>

```bash
sudo apt install ros-${ROS_DISTRO}-rosbridge-server
```
</details>


## 3.2. ROS環境でrosbridgeを起動します：


```bash
ros2 launch rosbridge_server rosbridge_websocket_launch.xml
```
> ⚠️ 特にカスタムメッセージやカスタムサービスを使用している場合は、起動する前にROSワークスペースを`source`することを忘れないでください。

</details>


---


# 4. 準備はできています！
どんなロボットでもサーバーをテストすることができます。ターゲットIPでロボットに接続するようにAIに指示するだけです。(デフォルトはlocalhostなので、MCPサーバーがROSと同じマシンにインストールされている場合は、接続を指示する必要はありません)

✅ **Tip:** 現在稼働中のロボットがない場合、turtlesimは実験用のhello-ROSロボットの一案です。GazeboやIsaacSimのようなシミュレーション依存性はありません。

MCPサーバーでturtlesimを使用するための完全なステップバイステップのチュートリアル、およびROSとturtlesimの詳細については、[Turtlesimチュートリアル](../examples/1_turtlesim/README.md)を参照してください。

ROSがすでにインストールされている場合は、以下のコマンドでturtlesimを起動できる：
**ROS1:**
```
rosrun turtlesim turtlesim_node
```

**ROS2:**
```
ros2 run turtlesim turtlesim_node
```


<details>
<summary><strong>コマンド例</strong></summary>

### 自然言語コマンド

Example:
```plaintext
Make the robot move forward.
```

<p align="center">
  <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/how_to_use_1.png" width="500"/>
</p>

### ROSシステムに問い合わせ
Example:  
```plaintext
What topics and services do you see on the robot?
```
<p align="center">
  <img src="https://github.com/robotmcp/ros-mcp-server/blob/main/docs/images/how_to_use_3.png" />
</p>

</details>
