import { useEffect, useState } from 'react'
import './App.css'

function App() {
  const [batteryData, setBatteryData] = useState(null);
  const [energyConsumptionData, setEnergyConsumptionData] = useState([]);
  const [postResponseEnergyConsumption, setPostResponseEnergyConsumption] = useState(null);
  const [postResponseBatteryData, setPostResponseBatteryData] = useState(null);

  useEffect(() => {
    fetchBatteryData();
    fetchEnergyConsumptionData();
  }, []);

  useEffect(() => {
    if (postResponseEnergyConsumption) {
      fetchEnergyConsumptionData();
    }
  }, [postResponseEnergyConsumption]);

  const fetchBatteryData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/battery/soc');
      const data = await response.json();
      setBatteryData(data);
      console.log('Battery data fetched:', data);
    } catch (error) {
      console.error('Error fetching battery data:', error);
    }
  };

  const fetchEnergyConsumptionData = async () => {
    try {
      const response = await fetch('http://127.0.0.1:8000/energy/consumption');
      const data = await response.json();
      setEnergyConsumptionData(data);
      console.log('Energy consumption data fetched:', data);
    } catch (error) {
      console.error('Error fetching energy consumption data:', error);
    }
  };

  const postEnergyConsumptionData = async (data) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/energy/consumption', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      setPostResponseEnergyConsumption(result);
      console.log('Energy consumption data posted:', result);
    } catch (error) {
      console.error('Error posting energy consumption data:', error);
    }
  };

  const postBatteryData = async (data) => {
    try {
      const response = await fetch('http://127.0.0.1:8000/battery/daily', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
      });
      const result = await response.json();
      setPostResponseBatteryData(result);
      console.log('Battery data posted:', result);
    } catch (error) {
      console.error('Error posting battery data:', error);
    }
  };

  return (
    <div className="App">
      <h1>SunMate Dashboard</h1>
      <div style={{ display: 'flex', gap: '20px' }}>
        <div className="data-section" style={{ flex: 1 }}>
          <h2>Battery Data</h2>
          {batteryData ? (
            <p>{batteryData.soc}% at {batteryData.timestamp}</p>
          ) : (
            <p>Loading battery data...</p>
          )}
          <div style={{ marginTop: '30px' }}>

            <h2>Post Battery Data</h2>
            <p>Enter battery data (one entry per line):
              <br />
              Format: Timestamp,SOC (e.g. 2024-11-29T00:00:00,85)
            </p>
            <form onSubmit={(e) => {
              e.preventDefault();
              const data = e.target.batteryData.value.split('\n').map(line => {
                const [timestamp, soc] = line.split(',');
                return { timestamp, soc: parseFloat(soc) };
              });
              postBatteryData(data);
            }}>
              <textarea name="batteryData" placeholder="Timestamp,SOC (e.g. 2024-11-29T00:00:00,85)" required />
              <button type="submit">Post Battery Data</button>
            </form>
            {postResponseBatteryData && (
              <p>
                Lowest SOC: {postResponseBatteryData.lowest_soc}
                <br />
                Highest SOC: {postResponseBatteryData.highest_soc}
                <br />
                SOC Difference: {postResponseBatteryData.soc_difference}
              </p>
            )}
          </div>
        </div>

        <div className="data-section" style={{ flex: 1 }}>
          <h2>Energy Consumption</h2>
          {energyConsumptionData.length > 0 ? (
            <ul style={{ listStyle: 'none', padding: 0 }}>
              {energyConsumptionData.map((entry, index) => (
                <li key={index}>
                  {entry.hour}: {entry.consumption_kwh} kWh
                </li>
              ))}
            </ul>
          ) : (
            <p>Loading energy consumption data...</p>
          )}
          <div style={{ marginTop: '30px' }}>
            <h2>Post Energy Consumption Data</h2>
            <form onSubmit={(e) => {
              e.preventDefault();
              const data = {
                timestamp: e.target.timestamp.value,
                consumption_kwh: parseFloat(e.target.consumption_kwh.value)
              };
              postEnergyConsumptionData(data);
            }}>
              <input type="text" name="timestamp" placeholder="Timestamp (e.g. 2024-11-29T00:00:00)" required />
              <input type="number" step="0.01" name="consumption_kwh" placeholder="Energy Consumption (kWh)" required />
              <button type="submit">Post Energy Consumption Data</button>
            </form>
            {postResponseEnergyConsumption && (
              <p>{postResponseEnergyConsumption.message}: {postResponseEnergyConsumption.consumption_kwh} kWh</p>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App
