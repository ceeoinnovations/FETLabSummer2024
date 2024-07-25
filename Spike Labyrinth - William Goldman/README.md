<h1> Build and Program the AI Spike Labyrinth</h1>
<h3>This project explores how different devices can connect to the Lego Spike Prime (uart). It is also an exploration of various AI algorithms, from Q-learning to OpenMV's blob detection.</h3>

###

<h2>DISCLAIMER</h2>
<p>This project is not yet finished, I have yet to integrate the AI algorithms into the program and Spike Motor control to actually physically move the ball from the chosen start square to end square.</p>

###

<h5>Materials:</h5>
<ul>
  <li>OpenMV Cam (I used an R2) with converter connector on the back -- this will connect to the black section of a lego ultrasonic sensor</li>
  <li>OpenMV IDE</li>
  <li>Visual Studio Code or another IDE to run pyscript on: Pyscript.com, Github Codespace with pyscript presetup, etc</li>
  <li>Lego Spike</li>
  <li><a href="https://www.brickowl.com/catalog/lego-spike-prime-set-45678/inventory">Lego pieces</a> (I used a combination of about 3 spike kits worth of parts)!
</li>
    <ul>
      <li>Two large Spike Motors</li>
      <li>One Spike Prime Hub</li>
      <li>Large Beams</li>
      <li>Right Angle Connectors</li>
      <li>Two Yellow Plates</li>
      <li>etc...</li>
    </ul>
  <li><a href="https://drive.google.com/file/d/1D8D3vNA3ystbz31rbjCMvUVYvHGMd4PP/view?usp=sharing">Instructions made by me for the model I built</a></li>
  <li>Some cord to connect the Spike to your computer (typically usb to micro usb)</li>
  <li><a href="https://raw.githack.com/tuftsceeo/SPIKE-html/main/index.html">Custom firmware (for uart communication)</a></li>
  <li><a href="https://github.com/chrisbuerginrogers/SPIKE_Prime/blob/main/BLE/BLE_CEEO.py#L1">BLE_CEEO.py</a> for establishing a bluetooth connection between your Spike and your computer</li>
</ul>

###

![spike labyrinth model render](https://github.com/user-attachments/assets/572d4f52-462e-4aab-9dce-a34d50dcdc79)
