using UnityEngine;
using System;
using UnityEngine.XR;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;

public class GyroscopeDataSender : MonoBehaviour
{
    private MqttClient client;
    private string brokerAddress = "broker.hivemq.com";
    private int brokerPort = 1883; // Default MQTT port
    private string topic = "oculus/gyroscope";

    private float publishInterval = 0.1f; // 100ms
    private float lastPublishTime = 0f;

    void Start()
    {
        // Initialize MQTT client
        client = new MqttClient(brokerAddress, brokerPort, false, null, null, MqttSslProtocols.None);
        
        string clientId = Guid.NewGuid().ToString();
        client.Connect(clientId);

        if (client.IsConnected)
        {
            Debug.Log("Connected to MQTT broker");
        }
        else
        {
            Debug.LogError("Failed to connect to MQTT broker");
        }
    }

    void Update()
    {
        if (client.IsConnected && Time.time - lastPublishTime >= publishInterval)
        {
            // Get rotation from the XR device
            InputDevice device = InputDevices.GetDeviceAtXRNode(XRNode.CenterEye);
            if (device.isValid)
            {
                Quaternion rotation;
                if (device.TryGetFeatureValue(CommonUsages.deviceRotation, out rotation))
                {
                    Vector3 eulerAngles = rotation.eulerAngles;

                    // Round angles to integers
                    int yaw = Mathf.RoundToInt(NormalizeAngle(eulerAngles.y));
                    int pitch = Mathf.RoundToInt(NormalizeAngle(eulerAngles.x));

                    // Format the message
                    string message = $"{yaw}, {pitch}";

                    // Publish the message
                    client.Publish(topic, System.Text.Encoding.UTF8.GetBytes(message));

                    // Update last publish time
                    lastPublishTime = Time.time;
                }
            }
        }
    }

    float NormalizeAngle(float angle)
    {
        // Ensure the angle is between 0 and 360
        while (angle < 0) angle += 360;
        while (angle >= 360) angle -= 360;
        return angle;
    }

    void OnApplicationQuit()
    {
        if (client != null && client.IsConnected)
        {
            client.Disconnect();
        }
    }
}
