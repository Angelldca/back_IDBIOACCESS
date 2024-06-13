from django.db import models

class Dciudadano(models.Model):
    idciudadano = models.AutoField(primary_key=True)
    area = models.CharField(max_length=150, blank=True, null=True)
    roluniversitario = models.CharField(max_length=100, blank=True, null=True)
    primernombre = models.CharField(max_length=100)
    segundonombre = models.CharField(max_length=100, blank=True, null=True)
    primerapellido = models.CharField(max_length=100)
    segundoapellido = models.CharField(max_length=100, blank=True, null=True)
    solapin = models.CharField(max_length=10, blank=True, null=True)
    carnetidentidad = models.CharField(max_length=35, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    sexo = models.CharField(max_length=35, blank=True, null=True)
    residente = models.BooleanField(blank=True, null=True)
    fechanacimiento = models.DateField(blank=True, null=True)
    idexpediente = models.CharField(max_length=20, blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    idpersona = models.OneToOneField('Dciudadanobash', models.DO_NOTHING, db_column='idpersona', blank=True, null=True)

    class Meta:
        db_table = 'dciudadano'
        
    def __str__(self):
        return self.primernombre
class Dcandidatos(models.Model):
    idincidencia = models.OneToOneField('Dincidenciasafis', models.DO_NOTHING, db_column='idincidencia', primary_key=True)  # The composite primary key (idincidencia, idciudbio) found, that is not supported. The first column is selected.
    fecha = models.DateTimeField(blank=True, null=True)
    idciudbio = models.IntegerField()
    class Meta:
       db_table = 'dcandidatos'
       unique_together = (('idincidencia', 'idciudbio'),)

class Dciudadanobash(models.Model):
    idexpediente = models.CharField(max_length=20)
    identificadorarea = models.CharField(max_length=150)
    identificadorroluni = models.CharField(max_length=100)
    carnetidentidad = models.CharField(max_length=35)
    fechanacimiento = models.DateField(blank=True, null=True)
    primernombre = models.CharField(max_length=100)
    segundonombre = models.CharField(max_length=100, blank=True, null=True)
    primerapellido = models.CharField(max_length=100)
    segundoapellido = models.CharField(max_length=100, blank=True, null=True)
    solapin = models.CharField(max_length=10, blank=True, null=True)
    provincia = models.CharField(max_length=100, blank=True, null=True)
    municipio = models.CharField(max_length=100, blank=True, null=True)
    sexo = models.CharField(max_length=30, blank=True, null=True)
    residente = models.BooleanField(blank=True, null=True)
    idestado = models.ForeignKey('Nestado', models.DO_NOTHING, db_column='idestado', blank=True, null=True)
    fecha_registro_modificacion = models.DateTimeField(blank=True, null=True)
    idpersona = models.CharField(primary_key=True, max_length=32)

    class Meta:
        db_table = 'dciudadanobash'
    def __str__(self):
        return self.primernombre


class Dciudadanosolapin(models.Model):
    idciudadano = models.OneToOneField(Dciudadano, on_delete=models.CASCADE, db_column='idciudadano', primary_key=True)  # The composite primary key (idciudadano, idsolapin) found, that is not supported. The first column is selected.
    idsolapin = models.OneToOneField('Dsolapin', models.DO_NOTHING, db_column='idsolapin')
    fecha = models.DateTimeField()

    class Meta:
       db_table = 'dciudadanosolapin'
       unique_together = (('idciudadano', 'idsolapin'),)


class Dciudadanosolapinhist(models.Model):
    idciudadanosolapinhist = models.AutoField(primary_key=True)
    idciudadano = models.ForeignKey(Dciudadano, on_delete=models.CASCADE, db_column='idciudadano')
    idsolapin = models.ForeignKey('Dsolapin', models.DO_NOTHING, db_column='idsolapin')
    fechaactivado = models.DateTimeField(blank=True, null=True)
    serialsolapin = models.CharField(max_length=10, blank=True, null=True)
    identificadoranulacion = models.ForeignKey('Ncausaanulacion', models.DO_NOTHING, db_column='identificadoranulacion', blank=True, null=True)
    idusuario = models.ForeignKey('Dusuario', models.DO_NOTHING, db_column='idusuario', blank=True, null=True)
    fechadesactivado = models.DateTimeField()
    codigobarra = models.CharField(max_length=10, blank=True, null=True)

    class Meta: 
        db_table = 'dciudadanosolapinhist'


class Dexcepcion(models.Model):
    idexcepcion = models.AutoField(primary_key=True)
    ipmaquina = models.CharField(max_length=20, blank=True, null=True)
    horaexcepcion = models.DateTimeField()
    nombreaplicacion = models.CharField(max_length=50, blank=True, null=True)
    usuarioaplicacion = models.CharField(max_length=50, blank=True, null=True)
    tipo = models.CharField(max_length=50, blank=True, null=True)
    mac = models.CharField(max_length=50, blank=True, null=True)
    mensaje = models.CharField(max_length=5000, blank=True, null=True)
    seccion = models.CharField(max_length=5000, blank=True, null=True)
    versionapp = models.CharField(max_length=50, blank=True, null=True)
    nombrepc = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        db_table = 'dexcepcion'


class Dhuellaciudadano(models.Model):
    idciudadano = models.OneToOneField(Dciudadano, on_delete=models.CASCADE, db_column='idciudadano', primary_key=True)  # The composite primary key (idciudadano, idtipohuella) found, that is not supported. The first column is selected.
    idtipohuella = models.ForeignKey('Ntipohuellaciudadano', models.DO_NOTHING, db_column='idtipohuella')
    huella = models.BinaryField()
    minucia = models.BinaryField()
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'dhuellaciudadano'
        unique_together = (('idciudadano', 'idtipohuella'),)


class Didentbiometrico(models.Model):
    idciudadano = models.IntegerField(blank=True, null=True)
    idbiometrico = models.UUIDField(unique=True)
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'didentbiometrico'


class Dimagenfacial(models.Model):
    idciudadano = models.OneToOneField(Dciudadano, on_delete=models.CASCADE, db_column='idciudadano', primary_key=True)
    foto = models.BinaryField()
    valida = models.BooleanField(blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    fecha_actualizacion = models.DateField(blank=True, null=True)
    def __str__(self):
        return self.idciudadano

    class Meta:
        db_table = 'dimagenfacial'


class Dincidenciasafis(models.Model):
    descripcion = models.CharField(max_length=200, blank=True, null=True)
    idincidencia = models.AutoField(primary_key=True)
    fecha = models.DateTimeField(blank=True, null=True)
    idsolicitudafis = models.ForeignKey('Dsolicitudafis', models.DO_NOTHING, db_column='idsolicitudafis', blank=True, null=True)

    class Meta:
        db_table = 'dincidenciasafis'

class Dnewsolapinhistorico(models.Model):
    idhistorico = models.AutoField(primary_key=True)
    idsolapin = models.IntegerField(blank=True, null=True)
    numerosolapin = models.CharField(max_length=7, blank=True, null=True)
    serial = models.CharField(max_length=10, blank=True, null=True)
    codigobarra = models.CharField(max_length=10, blank=True, null=True)
    idtiposolapin = models.IntegerField(blank=True, null=True)
    nombrecompleto = models.CharField(max_length=255, blank=True, null=True)
    area = models.CharField(max_length=150, blank=True, null=True)
    roluniversitario = models.CharField(max_length=100, blank=True, null=True)
    residente = models.BooleanField(blank=True, null=True)
    fecha = models.DateField(blank=True, null=True)
    datatiposolapin = models.CharField(max_length=255, blank=True, null=True, db_comment='Tipo de solapin segun la transformacion rol universirario')
    datacategoriasolapin = models.CharField(max_length=255, blank=True, null=True, db_comment='Categoria del solapin segun calsificacion rol universitario')
    idciudadano = models.IntegerField(blank=True, null=True)

    class Meta:
        db_table = 'dnewsolapinhistorico'


class Doperacionsolapin(models.Model):
    idoperacionsolapin = models.AutoField(primary_key=True)
    idsolapin = models.ForeignKey('Dsolapin', models.DO_NOTHING, db_column='idsolapin')
    codigobarra = models.CharField(max_length=10)
    numerosolapin = models.CharField(max_length=7)
    serial = models.CharField(max_length=10, blank=True, null=True)
    fechaoperacion = models.DateTimeField(unique=True)
    idusuario = models.ForeignKey('Dusuario', models.DO_NOTHING, db_column='idusuario')
    idcausaanulacion = models.ForeignKey('Ncausaanulacion', models.DO_NOTHING, db_column='idcausaanulacion', blank=True, null=True)
    idtipooperacionsolapin = models.ForeignKey('Ntipooperacionsolapin', models.DO_NOTHING, db_column='idtipooperacionsolapin')

    class Meta:
        db_table = 'doperacionsolapin'


class Doperacionsolicitud(models.Model):
    idoperacion = models.AutoField(primary_key=True)  # The composite primary key (idoperacion, fechaoperacion, idsolicitudimpresion) found, that is not supported. The first column is selected.
    fechaoperacion = models.DateTimeField()
    idsolicitudimpresion = models.ForeignKey('Dsolicitudimpresion', models.DO_NOTHING, db_column='idsolicitudimpresion')
    idestado = models.ForeignKey('Ntipoestadosolicitud', models.DO_NOTHING, db_column='idestado')
    idusuario = models.ForeignKey('Dusuario', models.DO_NOTHING, db_column='idusuario', blank=True, null=True)

    class Meta:
        db_table = 'doperacionsolicitud'
        unique_together = (('idoperacion', 'fechaoperacion', 'idsolicitudimpresion'),)


class Doperacionsolicitudhist(models.Model):
    idoperacion = models.AutoField(primary_key=True)  # The composite primary key (idoperacion, fechaoperacion) found, that is not supported. The first column is selected.
    fechaoperacion = models.DateTimeField()
    idsolicitudimpresion = models.ForeignKey('Dsolicitudimpresionhist',on_delete=models.CASCADE, db_column='idsolicitudimpresion')
    idestado = models.IntegerField()
    idusuario = models.ForeignKey('Dusuario', models.DO_NOTHING, db_column='idusuario', blank=True, null=True)

    class Meta:
        db_table = 'doperacionsolicitudhist'
        unique_together = (('idoperacion', 'fechaoperacion'),)


class Dordenimpresion(models.Model):
    idordenimpresion = models.AutoField(primary_key=True)
    numeroorden = models.CharField(max_length=30)
    fecha = models.DateField()
    idestadoorden = models.ForeignKey('Nestadoordenimpresion', models.DO_NOTHING, db_column='idestadoorden')
    tipoorden = models.CharField(max_length=30, blank=True, null=True)
    idordenspdi = models.CharField(max_length=40, blank=True, null=True)

    class Meta:
        db_table = 'dordenimpresion'


class Dordenimpresionhist(models.Model):
    idordenimpresion = models.AutoField(primary_key=True)
    numeroorden = models.CharField(max_length=30, blank=True, null=True)
    fecha = models.DateTimeField()
    tipoorden = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'dordenimpresionhist'


class Dsolapin(models.Model):
    idsolapin = models.AutoField(primary_key=True)
    codigobarra = models.CharField(max_length=10)
    numerosolapin = models.CharField(unique=True, max_length=7)
    serial = models.CharField(max_length=10, blank=True, null=True)
    estado = models.CharField(max_length=1, blank=True, null=True)
    idtiposolapin = models.ForeignKey('Ntiposolapin', models.DO_NOTHING, db_column='idtiposolapin', blank=True, null=True)
    fecha = models.DateTimeField(blank=True, null=True)
    def __str__(self):
        return self.numerosolapin

    class Meta:
        db_table = 'dsolapin'


class Dsolapinestado(models.Model):
    serial = models.CharField(max_length=10, blank=True, null=True)
    tiposol = models.IntegerField(blank=True, null=True)
    descripcionsol = models.CharField(max_length=50, blank=True, null=True)
    estadosol = models.IntegerField(blank=True, null=True)
    descripcionestado = models.CharField(max_length=25, blank=True, null=True)
    estadoreal = models.CharField(max_length=30, blank=True, null=True)
    ciudadano = models.IntegerField(blank=True, null=True)
    estado = models.CharField(max_length=1, blank=True, null=True)

    class Meta:
        db_table = 'dsolapinestado'


class Dsolicitudafis(models.Model):
    fecha = models.DateTimeField(blank=True, null=True)
    idsolicitudafis = models.UUIDField(primary_key=True)
    idntiposolicitudafis = models.ForeignKey('Ntiposolicitudafis', models.DO_NOTHING, db_column='idntiposolicitudafis', blank=True, null=True)
    estado = models.IntegerField(blank=True, null=True)
    idciudadano = models.ForeignKey(Dciudadano, models.DO_NOTHING, db_column='idciudadano', blank=True, null=True)

    class Meta:
        db_table = 'dsolicitudafis'


class Dsolicitudimpresion(models.Model):
    idsolicitudimpresion = models.AutoField(primary_key=True)
    numeroorden = models.CharField(max_length=30, blank=True, null=True)
    fechainicio = models.DateTimeField()
    idestado = models.ForeignKey('Ntipoestadosolicitud', models.DO_NOTHING, db_column='idestado', blank=True, null=True)
    idciudadano = models.ForeignKey(Dciudadano, models.DO_NOTHING, db_column='idciudadano')
    idusuario = models.ForeignKey('Dusuario', models.DO_NOTHING, db_column='idusuario', blank=True, null=True)

    class Meta:
        db_table = 'dsolicitudimpresion'


class Dsolicitudimpresionhist(models.Model):
    idsolicitudimpresion = models.AutoField(primary_key=True)
    fecha = models.DateTimeField()
    completado = models.CharField(max_length=1)
    idciudadano = models.ForeignKey(Dciudadano, db_column='idciudadano',on_delete=models.CASCADE)
    numeroorden = models.CharField(max_length=30, blank=True, null=True)
    idusuario = models.ForeignKey('Dusuario', models.DO_NOTHING, db_column='idusuario')
    fechacierre = models.DateTimeField()

    class Meta:
        db_table = 'dsolicitudimpresionhist'


class Dusuario(models.Model):
    idusuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, blank=True, null=True)
    usuario = models.CharField(max_length=24, blank=True, null=True)
    correo = models.CharField(max_length=100, blank=True, null=True)
    fechacreacion = models.DateTimeField(blank=True, null=True)
    estado = models.BooleanField(blank=True, null=True)
    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'dusuario'


class Dusuariopermiso(models.Model):
    idusuario = models.OneToOneField(Dusuario, models.DO_NOTHING, db_column='idusuario', primary_key=True)  # The composite primary key (idusuario, idtipopermiso) found, that is not supported. The first column is selected.
    idtipopermiso = models.ForeignKey('Ntipopermiso', models.DO_NOTHING, db_column='idtipopermiso')
    fecha = models.DateTimeField(blank=True, null=True)

    class Meta:
        db_table = 'dusuariopermiso'
        unique_together = (('idusuario', 'idtipopermiso'),)
        
class Dregistropago(models.Model):
    idregistropago = models.AutoField(primary_key=True)
    idciudadano = models.ForeignKey(Dciudadano, models.DO_NOTHING, db_column='idciudadano', blank=True, null=True)
    idsolapin = models.ForeignKey(Dsolapin, models.DO_NOTHING, db_column='idsolapin', blank=True, null=True)
    idusuario = models.IntegerField(blank=True, null=True)
    idcausaanulacion = models.ForeignKey('Ncausaanulacion', models.DO_NOTHING, db_column='identificadoranulacion')
    monto = models.IntegerField(blank=True, null=True)
    tipopago = models.CharField(max_length=255, blank=True, null=True)
    idtransferencia = models.CharField(max_length=255, blank=True, null=True)
    fecha = models.DateTimeField()
    
    class Meta:
        db_table = 'dregistropago'

class ExtradateTemp(models.Model):
    carnetidentidad = models.CharField(max_length=255, blank=True, null=True)
    nombrecompleto = models.CharField(max_length=255, blank=True, null=True)
    numexpediente = models.CharField(primary_key=True, max_length=255)
    anoacademico = models.CharField(max_length=255, blank=True, null=True)
    facultad = models.CharField(max_length=255, blank=True, null=True)
    grupo = models.CharField(max_length=255, blank=True, null=True)
    tipocurso = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = 'extradate_temp'


class Ncausaanulacion(models.Model):
    identificadoranulacion = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        db_table = 'ncausaanulacion'


class Nestado(models.Model):
    idestado = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=30, blank=True, null=True)

    class Meta:
        db_table = 'nestado'


class Nestadoordenimpresion(models.Model):
    idestadoorden = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=45)

    class Meta:
        db_table = 'nestadoordenimpresion'


class Ntipoestadosolicitud(models.Model):
    idestado = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=50)

    class Meta:
        db_table = 'ntipoestadosolicitud'


class Ntipohuellaciudadano(models.Model):
    idtipohuella = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=20)

    class Meta:
        db_table = 'ntipohuellaciudadano'


class Ntipooperacionsolapin(models.Model):
    idtipooperacionsolapin = models.IntegerField(primary_key=True)
    descripcion = models.CharField(unique=True, max_length=250)

    class Meta:
        db_table = 'ntipooperacionsolapin'


class Ntipopermiso(models.Model):
    idtipopermiso = models.IntegerField(primary_key=True)
    descripcion = models.CharField(max_length=250)
    recurso = models.CharField(max_length=250)

    class Meta:
        db_table = 'ntipopermiso'


class Ntiposolapin(models.Model):
    idtiposolapin = models.AutoField(primary_key=True)
    descripcion = models.CharField(blank=True, null=True)
    categoria = models.CharField(blank=True, null=True)

    class Meta:
        db_table = 'ntiposolapin'


class Ntiposolicitudafis(models.Model):
    idtiposolicitudafis = models.IntegerField(primary_key=True)
    descripcion = models.CharField(blank=True, null=True)
   

    class Meta:
        db_table = 'ntiposolicitudafis'

