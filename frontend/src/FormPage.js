import React from "react";
import { Button, Form, Segment, Input, Message, Progress } from "semantic-ui-react";

const FormPage = ({ onSubmit, onChange, loading, formData, error, progress }) => {
  const onFormChange = (e) => {
    const updatedData = {
      ...formData,
      [e.target.name]: e.target.value,
    };
    onChange(updatedData);
  };
  console.log(progress)

  return (
    <Segment>
      {error ? (
        <Message error>
          <Message.Header>Error</Message.Header>
          <Message.Content>{error}</Message.Content>
        </Message>
      ) : null}
      <Form loading={loading.form}>
        <Form.Field>
          <label>Location</label>
          <Input
            icon="crosshairs"
            loading={loading.location}
            iconPosition="left"
            name="from"
            value={formData.from}
            onChange={onFormChange}
            placeholder="Street, City"
          />
        </Form.Field>
        <Form.Field>
          <label>Max age of price (days)</label>
          <Input
            name="age"
            value={formData.age}
            onChange={onChange}
            placeholder="5"
          />
        </Form.Field>
        <Form.Field>
          <label>Max distance to the station</label>
          <Input
            name="distance"
            value={formData.distance}
            onChange={onChange}
            placeholder="20"
          />
        </Form.Field>
        <Form.Field>
          <label>Fuel consumption of car (l/100km)</label>
          <Input
            name="consumption"
            value={formData.consumption}
            onChange={onChange}
            placeholder="7.2"
          />
        </Form.Field>
        <Form.Field>
          <label>Amount to refill (litre)</label>
          <Input
            name="amount"
            value={formData.amount}
            onChange={onChange}
            placeholder="40"
          />
        </Form.Field>
        { !loading.form
          ? <Button size="large" onClick={() => onSubmit(formData)} primary>
            Find stations
          </Button>
          : <Progress percent={progress} /> }
      </Form>
    </Segment>
  );
};

export default FormPage;
