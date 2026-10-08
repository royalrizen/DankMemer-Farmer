# Dank Farmer <img src="https://cdn.discordapp.com/avatars/270904126974590976/cdf4f2cfaf99b4fc6bdbf050f917f6b2.png?size=4096" width=35>

An asynchronous Python script for automating **Dank Memer** commands and mini-games.

<br>

> [!CAUTION]
> Self-bots violate Discord's Terms of Service. Use at your own risk. I'm not responsible if your account gets suspended/banned from Discord or Dank Memer.


### Features?

- hunt, beg, dig
- high low, search, crime (It also has more chances of winning high low games.)
- humanized delays and typing indicator to avoid bot detection.
  
*More features are coming soon!*

---

### How to use?

**Step 1 - Download this repository and extract the .zip file.**
<br>

**Step 2 - Get your Discord credentials.**

1. Open Discord in your browser and press <kbd>F12</kbd> to open **Developer Tools**.
2. Go to the **Network** tab.
3. Send a message or click a button in your server.
4. Click on the `messages` or `interactions` request log.
5. Copy the values of `authorization`, `x-super-properties`, `x-context-properties`, and `x-installation-id` from the **Request Headers**.
<br>

**Step 3 - Rename the `.env.example` file to `.env` and add your credentials.**

```env
GUILD_ID="" # server where you want to farm
CHANNEL="" # channel of that server
APPLICATION_ID="270904126974590976" # Dank Memer's User ID

AUTH="YOUR_DISCORD_USER_TOKEN"
X_INSTALLATION_ID=""
X_CONTEXT_PROPERTIES=""
X_SUPER_PROPERTIES=""
```

> [!WARNING]
> Please **DO NOT** share these credentials with anyone or upload them to Github. Keep them safe.
> 
<br>

**Step 4 - Locate the repo directory.**

Run
```bash
pip install -e .
```
Start your Bot
```bash
farm
```
Have fun! ;)
Star the project if you liked it.
