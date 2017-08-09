from django.db import models
from django.contrib.auth.models import User

# Create your models here.


class Customer(models.Model):
    """客户信息表"""
    name = models.CharField(max_length=32, blank=True, null=True)
    qq = models.CharField(max_length=64, unique=True)
    qq_name = models.CharField(max_length=64, blank=True, null=True)
    phone = models.CharField(max_length=64, blank=True, null=True)
    source_choice = ((0, '转介绍'),
                     (1, 'QQ群'),
                     (2, '官网'),
                     (3, '百度推广'),
                     (4, '51CTO'),
                     (5, '知乎'),
                     (6, '市场推广')
                     )
    source = models.SmallIntegerField(choices=source_choice)
    referral_from = models.CharField(verbose_name='转介绍人qq', max_length=64, null=True, blank=True)
    consult_course = models.ForeignKey("Course", verbose_name="咨询课程", null=True, db_constraint=False)
    content = models.TextField(verbose_name="咨询详情")
    consultant = models.ForeignKey("UserProfile", db_constraint=False)
    date = models.DateTimeField(auto_now_add=True)
    memo = models.TextField(blank=True, null=True)
    status_choice = ((0, '已报名'),
                     (1, '未报名'),
                     )
    status = models.SmallIntegerField(choices=status_choice)
    tags = models.ManyToManyField(to="Tag", blank=True, db_constraint=False, )

    def __str__(self):
        return self.qq

    class Meta:
        verbose_name = "客户信息表"
        verbose_name_plural = "客户信息表"


class Tag(models.Model):
    """标签表"""
    name = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "标签表"
        verbose_name = "标签表"


class CustomerFollowUp(models.Model):
    """客户跟进表"""
    customer = models.ForeignKey("Customer", db_constraint=False)
    content = models.TextField(verbose_name="跟进内容")
    consultant = models.ForeignKey("UserProfile", db_constraint=False)
    intention_choices = ((0, '2周内报名'),
                         (1, '1个月内报名'),
                         (2, '近期元报名计划'),
                         (3, '已在其他机构报名'),
                         (4, '已报名'),
                         )
    intention = models.SmallIntegerField(choices=intention_choices)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "<%s %s>" % (self.customer.qq, self.intention)

    class Meta:
        verbose_name = "客户跟进表"
        verbose_name_plural = "客户跟进表"


class Course(models.Model):
    """课程表"""
    name = models.CharField(max_length=64, unique=True)
    price = models.PositiveIntegerField()
    period = models.PositiveSmallIntegerField(verbose_name="周期(月)")
    outline = models.TextField()  # 大纲

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "课程表"
        verbose_name_plural = "课程表"


class Branch(models.Model):
    """校区"""
    name = models.CharField(max_length=128, unique=True)
    addr = models.CharField(max_length=128)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "校区表"
        verbose_name_plural = "校区表"


class ClassList(models.Model):
    """班级表"""
    branch = models.ForeignKey("Branch", verbose_name="校区", db_constraint=False)
    course = models.ForeignKey("Course", db_constraint=False)
    class_type_choices = ((0, '面授(脱产)'),
                          (1, '面授(周末)'),
                          (2, '网络班'),
                          )
    class_type = models.PositiveSmallIntegerField(choices=class_type_choices, verbose_name="班级类型")
    semester = models.PositiveSmallIntegerField(verbose_name="学期")
    teachers = models.ManyToManyField("UserProfile", db_constraint=False)
    start_date = models.DateField(verbose_name="开班日期")
    end_date = models.DateField(verbose_name="结业日期", null=True, blank=True)

    def __str__(self):
        return "%s %s %s" % (self.branch, self.course, self.semester)

    class Meta:
        unique_together = ('branch', 'course', 'semester')
        verbose_name = "班级表"
        verbose_name_plural = "班级表"


class CourseRecord(models.Model):
    """上课记录"""
    from_class = models.ForeignKey("ClassList", verbose_name="班级", db_constraint=False)
    day_num = models.PositiveSmallIntegerField(verbose_name="第几节(天)")
    tercher = models.ForeignKey("UserProfile", db_constraint=False)
    has_homework = models.BooleanField(default=True)
    homework_title = models.CharField(max_length=128, null=True, blank=True)
    homework_content = models.TextField(blank=True, null=True)
    outline = models.TextField(verbose_name="本节大纲")
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.from_class, self.day_num)

    class Meta:
        unique_together = ("from_class", "day_num")
        verbose_name = "上课记录"
        verbose_name_plural = "上课记录"


class StudyRecode(models.Model):
    """学习记录表"""
    student = models.ForeignKey("Enrollment", db_constraint=False)
    course_recode = models.ForeignKey("CourseRecord", db_constraint=False)
    attendance_choices = (
        (0, "已签到"),
        (1, "迟到"),
        (2, "缺勤"),
        (3, "早退"),
    )
    attendance = models.PositiveSmallIntegerField(choices=attendance_choices, default=0)
    score_choices = (
        (100, 'A+'),
        (90, 'A'),
        (85, 'B+'),
        (80, 'B'),
        (75, 'B-'),
        (70, 'C+'),
        (60, 'C'),
        (40, 'C-'),
        (-50, 'D'),
        (-100, 'COPY'),
        (0, 'N/A'),
    )
    score = models.SmallIntegerField(choices=score_choices)
    memo = models.TextField(null=True)
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return "%s %s %s " % (self.student, self.course_recode, self.score)

    class Meta:
        unique_together = ("student", "course_recode")
        verbose_name = "学习记录表"
        verbose_name_plural = "学习记录表"


class Enrollment(models.Model):
    """报名表"""
    customer = models.ForeignKey("Customer", db_constraint=False)
    enrolled_class = models.ForeignKey("ClassList", verbose_name="所报班级", db_constraint=False)
    consultant = models.ForeignKey("UserProfile", verbose_name="课程顾问", db_constraint=False)
    contract_agreed = models.BooleanField(default=False, verbose_name="学员已同意合同条款")
    contract_approved = models.BooleanField(default=False, verbose_name="合同已审核")
    date = models.DateTimeField(auto_now_add=True,  verbose_name="报名时间")

    def __str__(self):
        return "%s %s" % (self.customer, self.enrolled_class)

    class Meta:
        unique_together = ("customer", "enrolled_class")
        verbose_name = "报名表"
        verbose_name_plural = "报名表"


class Payment(models.Model):
    """交费记录表"""
    customer = models.ForeignKey("Customer", db_constraint=False)
    course = models.ForeignKey("Course", verbose_name="所报课程", db_constraint=False)
    amount = models.PositiveIntegerField(verbose_name="数额", default=500)
    consultant = models.ForeignKey("UserProfile", db_constraint=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "%s %s" % (self.customer, self.amount)

    class Meta:
        verbose_name = "交费记录表"
        verbose_name_plural = "交费记录表"


class UserProfile(models.Model):
    """账户表"""
    user = models.OneToOneField(User)
    name = models.CharField(max_length=32)
    roles = models.ManyToManyField("Role", blank=True, db_constraint=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "账户表"
        verbose_name_plural = "账户表"


class Role(models.Model):
    """角色表"""
    name = models.CharField(max_length=32, unique=True)
    menus = models.ManyToManyField("Menu", blank=True, db_constraint=False)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "角色表"
        verbose_name_plural = "角色表"


class Menu(models.Model):
    """菜单表"""
    name = models.CharField(max_length=32)
    url_name = models.CharField(max_length=64)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "菜单表"
        verbose_name_plural = "菜单表"
