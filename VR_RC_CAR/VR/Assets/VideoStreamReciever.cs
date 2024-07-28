using UnityEngine;
using WebSocketSharp;
using System;
using System.Threading;

public class VideoStreamReceiver : MonoBehaviour
{
    public string serverUrl = "ws://your_server_ip:8765";
    
    [HideInInspector]
    public Texture2D leftEyeTexture;
    [HideInInspector]
    public Texture2D rightEyeTexture;

    private WebSocket ws;
    private byte[] leftImageData;
    private byte[] rightImageData;
    private bool dataReady = false;
    private object lockObject = new object();

    private void Start()
    {
        leftEyeTexture = new Texture2D(2, 2);
        rightEyeTexture = new Texture2D(2, 2);
        Debug.Log($"Textures created: {leftEyeTexture.width}x{leftEyeTexture.height}, {rightEyeTexture.width}x{rightEyeTexture.height}");

        ConnectToServer();
    }

    private void ConnectToServer()
    {
        ws = new WebSocket(serverUrl);

        ws.OnMessage += (sender, e) =>
        {
            ProcessVideoData(e.Data);
        };

        ws.OnOpen += (sender, e) =>
        {
            Debug.Log("WebSocket connection opened");
        };

        ws.OnError += (sender, e) =>
        {
            Debug.LogError($"WebSocket error: {e.Message}");
        };

        ws.OnClose += (sender, e) =>
        {
            Debug.Log($"WebSocket closed: {e.Reason}");
        };

        ws.Connect();
        Debug.Log("WebSocket connection attempted");
    }

    private void ProcessVideoData(string data)
    {
        string[] splitData = data.Split('|');
        if (splitData.Length != 2)
        {
            Debug.LogError("Received invalid data format");
            return;
        }

        try
        {
            byte[] leftData = Convert.FromBase64String(splitData[0]);
            byte[] rightData = Convert.FromBase64String(splitData[1]);

            lock (lockObject)
            {
                leftImageData = leftData;
                rightImageData = rightData;
                dataReady = true;
            }

            Debug.Log($"Received frame data. Left: {leftData.Length} bytes, Right: {rightData.Length} bytes");
        }
        catch (Exception e)
        {
            Debug.LogError($"Error processing video data: {e.Message}");
        }
    }

    private void Update()
    {
        if (dataReady)
        {
            lock (lockObject)
            {
                UpdateTexture(leftEyeTexture, leftImageData);
                UpdateTexture(rightEyeTexture, rightImageData);
                dataReady = false;
            }
        }
    }

    private void UpdateTexture(Texture2D texture, byte[] imageData)
    {
        if (imageData != null && imageData.Length > 0)
        {
            if (texture.LoadImage(imageData))
            {
                Debug.Log($"Texture updated: {texture.width}x{texture.height}");
            }
            else
            {
                Debug.LogError("Failed to load image data into texture");
            }
        }
    }

    private void OnDestroy()
    {
        if (ws != null && ws.IsAlive)
        {
            ws.Close();
        }
    }
}