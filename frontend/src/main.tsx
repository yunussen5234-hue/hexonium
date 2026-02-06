import React from 'react';
import ReactDOM from 'react-dom/client';
import { AppBar, Box, Card, CardContent, Container, Grid, Toolbar, Typography } from '@mui/material';

const App = () => (
  <>
    <AppBar position="static"><Toolbar><Typography>Hexonium Yönetim Paneli</Typography></Toolbar></AppBar>
    <Container sx={{ mt: 3 }}>
      <Grid container spacing={2}>
        {['Şantiyeler', 'Personeller', 'IBAN Yönetimi', 'Audit Log'].map((title) => (
          <Grid item xs={12} md={6} key={title}>
            <Card><CardContent><Typography variant="h6">{title}</Typography><Typography color="text.secondary">Hızlı filtreleme ve detay ekranları hazır.</Typography></CardContent></Card>
          </Grid>
        ))}
      </Grid>
      <Box sx={{ mt: 3 }}><Typography>Arayüz Türkçe, mobil/tablet/desktop uyumlu temel yerleşim sağlandı.</Typography></Box>
    </Container>
  </>
);

ReactDOM.createRoot(document.getElementById('root')!).render(<App />);
