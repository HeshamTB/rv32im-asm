.text
main:
	addi a1, zero, 0xff
	sb t1, -100(t2)
	addi t1, a1, 25
	xor  t2, t1, a1
	lw	t2, 0(t0)
	lui t1, 500
	jal ra, print
print:
	addi a0, zero, 1
	add  a1, t1, zero
	addi a2, zero, 32
	jal ra, print
	addi a7, zero, 64
	beq a7, zero, print
	ecall
	
L3:
	add t1, a0, a1
	bne t1, a0, L3

.data
msg: .ascii "Test Sent"
