# How to Set Up the Raspberry Pi as a Self-Hosted Runner

Since we switched the workflow to `runs-on: self-hosted`, your Raspberry Pi now needs to listen for jobs from GitHub.

## 1. Create the Runner on GitHub

1.  Go to your Repository on GitHub.
2.  Click **Settings** (top bar).
3.  Click **Actions** (left sidebar) -> **Runners**.
4.  Click **New self-hosted runner**.
5.  Select **Linux** and **ARM64**.

## 2. Install on Raspberry Pi

Open your SSH terminal on the Pi and run the commands GitHub gives you. They will look exactly like this:

```bash
# 1. Create a folder
mkdir actions-runner && cd actions-runner

# 2. Download the runner (Use the specific curl command from GitHub page!)
curl -o actions-runner-linux-arm64-....tar.gz -L https://github.com/actions/runner/...

# 3. Extract
tar xzf ./actions-runner-linux-arm64-*.tar.gz

# 4. Configure (You will need the 'token' from the GitHub page)
./config.sh --url https://github.com/Volp02/64Matrix --token <YOUR_TOKEN>
# Just press [Enter] for all the questions (default name, default group, etc.)
```

## 3. Install as a Service (Crucial!)

You want this to run automatically when the Pi boots.

```bash
# Install the service
sudo ./svc.sh install

# Start the service
sudo ./svc.sh start
```

## 4. Done!

You should see "Idle" next to the runner in GitHub Settings.
Now, when you push a Release Tag (v0.0.X), your Pi will wake up and build the Docker image itself!
