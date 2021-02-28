import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Divider, Header } from "semantic-ui-react";
import "semantic-ui-css/semantic.min.css";
import FormPage from "./FormPage";
import StationsList from "./StationList";
import { usePosition, useInterval } from "./hooks";
import geocode from "./geocode";

const BASE_URL =
  process.env.NODE_ENV === "development"
    ? "http://localhost:8000/api"
    : `https://${new URL(window.location).hostname}/api`;

const api = axios.create({ baseURL: BASE_URL });

const INITAL_STATE = {
  from: "",
  age: 5,
  distance: 20,
  consumption: 7.2,
  amount: 40,
};

const styles = {
  appBar: {
    padding: "1rem",
    boxShadow: "0 2px 4px 0 rgba(0,0,0,.15)",
    marginBottom: "1.5rem",
  },
};

const App = () => {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState({
    form: false,
    location: false,
  });
  const [error, setError] = useState(null);
  const [formData, setFormData] = useState(INITAL_STATE);
  const [interval, setIntervalValue] = useState(null);
  const [progress, setProgress] = useState(0);
  const { position } = usePosition();

  const fetchLocation = async () => {
    if (formData.location || stations.length) return;
    setLoading({ ...loading, location: true });
    const from = await geocode(position.latitude, position.longitude);
    setFormData({ ...formData, from });
    setLoading({ ...loading, location: false });
  };

  useEffect(() => {
    fetchLocation();
  }, [position]); //eslint-disable-line

  useInterval(
    () => setProgress((currentProgress) => currentProgress + 1),
    interval
  );

  const resetFormLoading = () => {
    setIntervalValue(null);
    setProgress(0);
    setLoading({ ...loading, form: false });
  };

  const fetchStations = async (formData) => {
    try {
      setLoading({ ...loading, form: true });
      setIntervalValue(40 * 10);
      const { data } = await api.post("", formData);
      setStations(data);
      resetFormLoading();
    } catch (e) {
      console.log(e);
      setError(e.toString());
      resetFormLoading();
    }
  };

  const renderStations = () => (
    <StationsList
      stations={stations.slice(0, 5)}
      amount={"40"}
      clearData={() => setStations([])}
      stationsAmount={5}
      origin={formData.from}
    />
  );
  const renderForm = () =>
    !stations || !stations.length ? (
      <>
        <Header as="h3">Usage</Header>
        <p>
          Find cheapest gas station near you. Cheapest total price will include{" "}
          the price of gasoline as well as the price of driving to the stations{" "}
          and back.
        </p>
        <Divider hidden />
        <FormPage
          formData={formData}
          onSubmit={fetchStations}
          onChange={setFormData}
          error={error}
          progress={progress}
          loading={loading}
        />
      </>
    ) : null;

  return (
    <div style={{ paddingBottom: "2rem" }}>
      <div style={styles.appBar}>
        <Header as="h2">Gasoline</Header>
      </div>
      <Container>
        {renderStations()}
        {renderForm()}
      </Container>
    </div>
  );
};

export default App;
