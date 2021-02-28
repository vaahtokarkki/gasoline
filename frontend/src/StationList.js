import React, { useState } from "react";
import { Button, Segment, List, Table } from "semantic-ui-react";

function getRouteUrl(origin, dest) {
  return `https://www.google.com/maps/dir/?api=1&origin=${origin}&destination=${dest}`;
}

function resolveColor(value) {
  if (value < 1.5) return "#016936";
  if (value < 1.55) return "#FE9A76";
  return "#B03060";
}

const ListItem = ({ item, amount, origin }) => (
  <List.Item key={item.name}>
    <List.Content floated="right"></List.Content>
    <List.Content style={{ padding: ".75rem 0 0 0" }}>
      <div style={{ display: "flex" }}>
        <div style={{ width: "70%", paddingRight: 20 }}>
          <b>{item.name}</b> ({item.price_age})
          <div style={{ margin: "5px 0" }}>
            <Button
              size="tiny"
              onClick={() => {
                window.open(getRouteUrl(`${item.lat},${item.lon}`, origin));
              }}
            >
              Google Maps
            </Button>
          </div>
        </div>
        <div>
          <Table celled unstackable compact basic='very' >
            <Table.Body>
              <Table.Row>
                <Table.Cell>95E10</Table.Cell>
                <Table.Cell
                  style={{
                    fontWeight: "bold",
                    color: resolveColor(item["95E10/l"]),
                  }}
                >
                  {item["95E10/l"]}e/l
                </Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>{amount}l (car)</Table.Cell>
                <Table.Cell>{item.total_price}e</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell>{amount}l</Table.Cell>
                <Table.Cell>{item.only_gas}e</Table.Cell>
              </Table.Row>
              <Table.Row>
                <Table.Cell colSpan="2">
                  {item.distance}km, {item.durations}min
                </Table.Cell>
              </Table.Row>
            </Table.Body>
          </Table>
        </div>
      </div>
    </List.Content>
  </List.Item>
);

const StationsList = ({ stations, amount, clearData, origin }) => {
  const [sortBy, setSortBy] = useState("total_price");
  if (!stations || !stations.length) return null;

  return (
    <>
      <Segment>
        <h3>Stations</h3>
        <p>Sort by lowest:</p>
        <Button.Group style={{ marginBottom: "1rem" }} size="tiny">
          <Button
            onClick={() => setSortBy("total_price")}
            active={sortBy === "total_price"}
          >
            Price
          </Button>
          <Button
            onClick={() => setSortBy("95E10/l")}
            active={sortBy === "95E10/l"}
          >
            Price per l
          </Button>
          <Button
            onClick={() => setSortBy("distance")}
            active={sortBy === "distance"}
          >
            Distance
          </Button>
        </Button.Group>

        <List divided verticalAlign="middle">
          {stations
            .sort((a, b) => a[sortBy] - b[sortBy])
            .map((s) => (
              <ListItem key={s.name} item={s} amount={amount} origin={origin} />
            ))}
        </List>
      </Segment>
      <Button size="big" onClick={clearData} primary>
        New search
      </Button>
    </>
  );
};

export default StationsList;
