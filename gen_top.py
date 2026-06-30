#!/usr/bin/env python3
import random
import sys

random.seed(45)

N_IN = 64
N_OUT = 64
N_REG = 256
N_COMB = 900


def w(s, line=""):
    s.write(line + "\n")


def emit_header(s):
    ports = ["clk", "rst_n", "set_n"]
    ports += [f"in{i}" for i in range(N_IN)]
    ports += [f"out{i}" for i in range(N_OUT)]
    w(s, f"module top ({', '.join(ports)});")
    w(s, "  input clk;")
    w(s, "  input rst_n;")
    w(s, "  input set_n;")
    for i in range(N_IN):
        w(s, f"  input in{i};")
    for i in range(N_OUT):
        w(s, f"  output out{i};")
    w(s)


def emit_decls(s):
    w(s, "  wire nclk;")
    w(s, "  wire gnd;")
    w(s, "  wire vdd;")
    w(s, "  assign gnd = 1'b0;")
    w(s, "  assign vdd = 1'b1;")
    w(s)

    for i in range(N_REG):
        w(s, f"  wire q{i};")
    for i in range(N_REG):
        w(s, f"  wire r{i};")
    for i in range(N_REG):
        w(s, f"  wire s{i};")
    for i in range(N_REG):
        w(s, f"  wire t{i};")
    for i in range(N_REG):
        w(s, f"  wire u{i};")
    w(s)


def emit_inputs(s):
    w(s, "  INV_X1 UCLKINV (.A(clk), .ZN(nclk));")
    w(s, "  BUF_X1 URSTBUF (.A(rst_n), .Z(s0));")
    w(s, "  BUF_X1 USETBUF (.A(set_n), .Z(s1));")
    for i in range(min(N_IN, 64)):
        w(s, f"  BUF_X1 UINBUF_{i:03d} (.A(in{i}), .Z(q{i}));")
    w(s)


def emit_regs(s):
    reg_types = [
        "DFF_X1",
        "DFF_X2",
        "DFFR_X1",
        "DFFR_X2",
        "DFFS_X1",
        "DFFS_X2",
        "DFFRS_X1",
        "DFFRS_X2",
    ]
    for i in range(N_REG):
        cell = random.choice(reg_types)
        d = f"q{random.randrange(min(N_IN, 64))}"
        if cell in ("DFF_X1", "DFF_X2"):
            w(s, f"  {cell} UFF_{i:04d} (.D({d}), .CK(clk), .Q(r{i}), .QN());")
        elif cell.startswith("DFFR"):
            w(s, f"  {cell} UFF_{i:04d} (.D({d}), .CK(clk), .RN(rst_n), .Q(r{i}), .QN());")
        elif cell.startswith("DFFS") and not cell.startswith("DFFRS"):
            w(s, f"  {cell} UFF_{i:04d} (.D({d}), .CK(clk), .SN(set_n), .Q(r{i}), .QN());")
        else:
            w(s, f"  {cell} UFF_{i:04d} (.D({d}), .CK(clk), .RN(rst_n), .SN(set_n), .Q(r{i}), .QN());")
    w(s)


def emit_comb(s):
    combo_types = [
        "BUF_X1", "BUF_X2", "BUF_X4", "BUF_X8",
        "INV_X1", "INV_X2", "INV_X4", "INV_X8",
        "NAND2_X1", "NAND2_X2", "NAND2_X4",
        "NOR2_X1", "NOR2_X2", "NOR2_X4",
        "AND2_X1", "AND2_X2", "AND2_X4",
        "OR2_X1", "OR2_X2", "OR2_X4",
        "XOR2_X1", "XNOR2_X1",
        "MUX2_X1", "MUX2_X2",
        "AOI21_X1", "AOI21_X2", "AOI21_X4",
        "OAI21_X1", "OAI21_X2", "OAI21_X4",
        "AOI22_X1", "AOI22_X2", "AOI22_X4",
        "OAI22_X1", "OAI22_X2", "OAI22_X4",
        "AOI211_X1", "AOI211_X2", "AOI211_X4",
        "OAI211_X1", "OAI211_X2", "OAI211_X4",
        "AOI221_X1", "AOI221_X2", "AOI221_X4",
        "OAI221_X1", "OAI221_X2", "OAI221_X4",
        "AOI222_X1", "AOI222_X2", "AOI222_X4",
        "OAI222_X1", "OAI222_X2", "OAI222_X4",
        "NAND3_X1", "NOR3_X1", "AND3_X1", "OR3_X1",
        "NAND4_X1", "NOR4_X1", "AND4_X1", "OR4_X1",
    ]
    sources = [f"q{i}" for i in range(N_REG)] + [f"r{i}" for i in range(N_REG)] + [f"s{i}" for i in range(N_REG)]
    built = []
    for i in range(N_COMB):
        cell = random.choice(combo_types)
        out = f"t{i % N_REG}"
        a = random.choice((sources + built) if built else sources)
        b = random.choice((sources + built) if built else sources)
        c = random.choice((sources + built) if built else sources)
        d = random.choice((sources + built) if built else sources)

        if cell.startswith(("BUF", "INV")):
            outpin = ".Z" if cell.startswith("BUF") else ".ZN"
            w(s, f"  {cell} UC_{i:04d} (.A({a}), {outpin}({out}));")
        elif cell in ["XOR2_X1", "XNOR2_X1"]:
            outpin = ".Z" if cell == "XOR2_X1" else ".ZN"
            w(s, f"  {cell} UC_{i:04d} (.A({a}), .B({b}), {outpin}({out}));")
        elif cell in ["NAND2_X1", "NAND2_X2", "NAND2_X4", "NOR2_X1", "NOR2_X2", "NOR2_X4", "AND2_X1", "AND2_X2", "AND2_X4", "OR2_X1", "OR2_X2", "OR2_X4"]:
            outpin = ".ZN" if cell.startswith(("NAND", "NOR", "AND", "OR")) else ".Z"
            w(s, f"  {cell} UC_{i:04d} (.A1({a}), .A2({b}), {outpin}({out}));")
        elif cell.startswith("MUX2"):
            w(s, f"  {cell} UC_{i:04d} (.A({a}), .B({b}), .S({c}), .Z({out}));")
        elif cell in ["AOI21_X1", "AOI21_X2", "AOI21_X4", "OAI21_X1", "OAI21_X2", "OAI21_X4"]:
            w(s, f"  {cell} UC_{i:04d} (.A({a}), .B1({b}), .B2({c}), .ZN({out}));")
        elif cell in ["AOI22_X1", "AOI22_X2", "AOI22_X4", "OAI22_X1", "OAI22_X2", "OAI22_X4"]:
            w(s, f"  {cell} UC_{i:04d} (.A1({a}), .A2({b}), .B1({c}), .B2({d}), .ZN({out}));")
        elif cell in ["AOI211_X1", "AOI211_X2", "AOI211_X4", "OAI211_X1", "OAI211_X2", "OAI211_X4"]:
            w(s, f"  {cell} UC_{i:04d} (.A({a}), .B({b}), .C1({c}), .C2({d}), .ZN({out}));")
        elif cell in ["AOI221_X1", "AOI221_X2", "AOI221_X4", "OAI221_X1", "OAI221_X2", "OAI221_X4"]:
            w(s, f"  {cell} UC_{i:04d} (.A({a}), .B1({b}), .B2({c}), .C1({d}), .C2({a}), .ZN({out}));")
        elif cell in ["AOI222_X1", "AOI222_X2", "AOI222_X4", "OAI222_X1", "OAI222_X2", "OAI222_X4"]:
            w(s, f"  {cell} UC_{i:04d} (.A1({a}), .A2({b}), .B1({c}), .B2({d}), .C1({a}), .C2({b}), .ZN({out}));")
        elif cell in ["NAND3_X1", "NOR3_X1", "AND3_X1", "OR3_X1"]:
            w(s, f"  {cell} UC_{i:04d} (.A1({a}), .A2({b}), .A3({c}), .ZN({out}));")
        elif cell in ["NAND4_X1", "NOR4_X1", "AND4_X1", "OR4_X1"]:
            w(s, f"  {cell} UC_{i:04d} (.A1({a}), .A2({b}), .A3({c}), .A4({d}), .ZN({out}));")
        built.append(out)
    w(s)


def emit_register_banks(s):
    for i in range(N_REG):
        src = f"t{i}"
        if i % 4 == 0:
            w(s, f"  DFF_X1 UREG_{i:04d} (.D({src}), .CK(clk), .Q(s{i}), .QN());")
        elif i % 4 == 1:
            w(s, f"  DFF_X2 UREG_{i:04d} (.D({src}), .CK(clk), .Q(s{i}), .QN());")
        elif i % 4 == 2:
            w(s, f"  DFFR_X1 UREG_{i:04d} (.D({src}), .CK(clk), .RN(rst_n), .Q(s{i}), .QN());")
        else:
            w(s, f"  DFFRS_X1 UREG_{i:04d} (.D({src}), .CK(clk), .RN(rst_n), .SN(set_n), .Q(s{i}), .QN());")
    w(s)


def emit_outputs(s):
    for i in range(N_OUT):
        a = f"s{(i * 3) % N_REG}"
        b = f"r{(i * 5) % N_REG}"
        c = f"q{(i * 7) % N_REG}"
        if i % 4 == 0:
            w(s, f"  BUF_X4 UOUT_{i:03d} (.A({a}), .Z(out{i}));")
        elif i % 4 == 1:
            w(s, f"  XOR2_X1 UOUT_{i:03d} (.A({a}), .B({b}), .Z(out{i}));")
        elif i % 4 == 2:
            w(s, f"  MUX2_X1 UOUT_{i:03d} (.A({a}), .B({b}), .S({c}), .Z(out{i}));")
        else:
            w(s, f"  AOI21_X1 UOUT_{i:03d} (.A({a}), .B1({b}), .B2({c}), .ZN(out{i}));")


def emit_footer(s):
    w(s, "endmodule")


def main():
    s = sys.stdout
    emit_header(s)
    emit_decls(s)
    emit_inputs(s)
    emit_regs(s)
    emit_comb(s)
    emit_register_banks(s)
    emit_outputs(s)
    emit_footer(s)


if __name__ == "__main__":
    main()
