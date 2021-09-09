# Gym

What I had to do to install gym in my virtual environment (Big Sur, Apple M1 chip, Python 3.8.2): 

1. Make sure that pip is up-to-date.
2. Install wheel: `pip3 install wheel` 
3. Install scipy: `pip3 install scipy`. This was very difficult for me for some reason (perhaps the operating system, Big Sur, or the Apple M1 chip): simply installing it using pip didn't work, so I tried many suggestions, but what ultimately worked was this: https://github.com/scipy/scipy/issues/13102#issuecomment-731621271. 
   1. Download the most recent scipy wheel file for the respective system from here: pypi.org/project/scipy/#files (in my case `scipy-1.7.1-cp38-cp38-macosx_10_9_x86_64.whl`) 
   2. Put it in the repo's root directory 
   3. Rename it so the system doesn't reject it, e.g. `scipy-1.7.1-cp38-none-any.whl` 
   4. Run `pip3 install scipy-1.7.1-cp38-none-any.whl` 
   5. Delete the wheel file `scipy-1.7.1-cp38-none-any.whl`
4. Install Pillow `pip3 install Pillow` (you might have to install external libraries via brew first and make sure that all external libraries are installed, https://github.com/GetStream/django_twitter/issues/31#issuecomment-544313101)  
   1. Install `homebrew` by running `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`  
   2. Make sure that `brew` is on `PATH`. If not, then running `brew` would return `zsh: command not found: brew`. In this case, you can add it to `PATH` by running this: `export PATH=/opt/homebrew/bin:$PATH`.
   3. `brew install gcc` (not sure if necessary)
   4. `brew install libtiff libjpeg webp little-cms2` 
   5. `brew install freetype harfbuzz fribidi`
5. Install gym: `pip3 install gym`