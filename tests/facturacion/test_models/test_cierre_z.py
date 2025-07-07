from django.test import TestCase
from facturacion.models import CierreZ
from datetime import date, timedelta

class CierreZModelTest(TestCase):
    def setUp(self):
        self.cierre_data = {
            'fecha': date.today(),
            'cant_doc_fiscales': 10,
            'cant_doc_fiscales_a_emitidos': 5,
            'cant_doc_fiscales_bc_emitidos': 3,
            'cant_doc_fiscales_cancelados': 2,
            'cant_doc_nofiscales': 0,
            'cant_doc_nofiscales_homologados': 0,
            'cant_nc_a_fiscales_a_emitidos': 1,
            'cant_nc_bc_emitidos': 1,
            'cant_nc_canceladas': 0,
            'monto_credito_nc': 100.50,
            'monto_imp_internos': 50.25,
            'monto_imp_internos_nc': 10.05,
            'monto_iva_doc_fiscal': 210.00,
            'monto_iva_nc': 21.00,
            'monto_iva_no_inscripto': 0.00,
            'monto_iva_no_inscripto_nc': 0.00,
            'monto_percepciones': 42.00,
            'monto_percepciones_nc': 4.20,
            'monto_ventas_doc_fiscal': 1000.00,
            'status_fiscal': '0600',
            'status_impresora': 'C080',
            'ultima_nc_a': 30,
            'ultima_nc_b': 327,
            'ultimo_doc_a': 2262,
            'ultimo_doc_b': 66733,
            'ultimo_remito': 0,
            'zeta_numero': 1
        }
        self.cierre = CierreZ.objects.create(**self.cierre_data)
    
    def test_creacion_cierre_z(self):
        """Test de creación básica de un cierre Z"""
        self.assertEqual(CierreZ.objects.count(), 1)
        cierre = CierreZ.objects.first()
        self.assertEqual(cierre.fecha, self.cierre_data['fecha'])
        self.assertEqual(cierre.cant_doc_fiscales, 10)
        self.assertEqual(cierre.monto_ventas_doc_fiscal, 1000.00)
        self.assertEqual(cierre.status_fiscal, '0600')
    
    def test_valores_por_defecto(self):
        """Test de los valores por defecto del cierre Z"""
        cierre = CierreZ.objects.create()
        self.assertEqual(cierre.RESERVADO_SIEMPRE_CERO, 0)
        self.assertEqual(cierre.cant_doc_fiscales, 0)
        self.assertEqual(cierre.cant_doc_fiscales_a_emitidos, 0)
        self.assertEqual(cierre.cant_doc_fiscales_bc_emitidos, 0)
        self.assertEqual(cierre.cant_doc_fiscales_cancelados, 0)
        self.assertEqual(cierre.cant_doc_nofiscales, 1)  # Valor por defecto es 1
        self.assertEqual(cierre.cant_doc_nofiscales_homologados, 0)
        self.assertEqual(cierre.cant_nc_a_fiscales_a_emitidos, 0)
        self.assertEqual(cierre.cant_nc_bc_emitidos, 0)
        self.assertEqual(cierre.cant_nc_canceladas, 0)
        self.assertEqual(cierre.monto_credito_nc, 0.00)
        self.assertEqual(cierre.monto_imp_internos, 0.00)
        self.assertEqual(cierre.monto_imp_internos_nc, 0.00)
        self.assertEqual(cierre.monto_iva_doc_fiscal, 0.00)
        self.assertEqual(cierre.monto_iva_nc, 0.00)
        self.assertEqual(cierre.monto_iva_no_inscripto, 0.00)
        self.assertEqual(cierre.monto_iva_no_inscripto_nc, 0.00)
        self.assertEqual(cierre.monto_percepciones, 0.00)
        self.assertEqual(cierre.monto_percepciones_nc, 0.00)
        self.assertEqual(cierre.monto_ventas_doc_fiscal, 0.00)
        self.assertEqual(cierre.status_fiscal, '0600')
        self.assertEqual(cierre.status_impresora, 'C080')
        self.assertEqual(cierre.ultima_nc_a, 30)
        self.assertEqual(cierre.ultima_nc_b, 327)
        self.assertEqual(cierre.ultimo_doc_a, 2262)
        self.assertEqual(cierre.ultimo_doc_b, 66733)
        self.assertEqual(cierre.ultimo_remito, 0)
        self.assertEqual(cierre.zeta_numero, 1)
    
    def test_str_representation(self):
        """Test de la representación en string del modelo"""
        fecha_str = self.cierre.fecha.strftime('%Y-%m-%d')
        expected_str = f"FiscalZ {fecha_str}"
        self.assertEqual(str(self.cierre), expected_str)
    
    def test_fecha_auto_ahora(self):
        """Test de que la fecha se establece automáticamente al crear"""
        hoy = date.today()
        cierre = CierreZ.objects.create()
        self.assertEqual(cierre.fecha, hoy)
    
    def test_incremento_zeta_numero(self):
        """Test de que zeta_numero no se incrementa automáticamente"""
        cierre1 = CierreZ.objects.create()
        cierre2 = CierreZ.objects.create()
        # El zeta_numero no se incrementa automáticamente, debe ser manejado manualmente
        self.assertEqual(cierre2.zeta_numero, cierre1.zeta_numero)
        
        # Para probar el incremento manual
        cierre3 = CierreZ.objects.create(zeta_numero=cierre2.zeta_numero + 1)
        self.assertEqual(cierre3.zeta_numero, cierre2.zeta_numero + 1)
