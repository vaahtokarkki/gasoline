import React, { useState, useEffect } from "react";
import axios from "axios";
import { Container, Divider, Header } from "semantic-ui-react";
import "semantic-ui-css/semantic.min.css";
import FormPage from "./FormPage";
import StationsList from "./StationList";
import { usePosition } from "./hooks";
import geocode from "./geoCode";

const BASE_URL =
  process.env.NODE_ENV === "development" ? "http://localhost:8000/api" : "/api";

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
  const { position } = usePosition();

  const fetchLocation = async () => {
    if (formData.location) return;
    setLoading({ ...loading, location: true });
    const from = await geocode(position.latitude, position.longitude);
    setFormData({ ...formData, from });
    setLoading({ ...loading, location: false });
  };

  useEffect(() => {
    fetchLocation();
  }, [position]); //eslint-disable-line

  const fetchStations = async (formData) => {
    try {
      setLoading({ ...loading, form: true });
      const { data } = await api.post("/", formData);
      setStations(data);
      setLoading({ ...loading, form: false });
    } catch (e) {
      console.log(e);
      setError(e.toString());
      setLoading({ ...loading, form: false });
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
          A container is a fixed width element that wraps your site's content.
          It remains a constant size and uses <b>margin</b> to center.
          Containers are the simplest way to center page content inside a grid.
        </p>
        <Divider hidden />
        <FormPage
          formData={formData}
          onSubmit={fetchStations}
          onChange={setFormData}
          error={error}
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
